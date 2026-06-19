"""Perception layer — live CMC + public signals with divergence detection."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from agents.types import MarketSnapshot
from config.settings import Settings

logger = logging.getLogger(__name__)

CMC_REST_BASE = "https://pro-api.coinmarketcap.com"
FNG_PUBLIC_URL = "https://api.alternative.me/fng/?limit=1"


class PerceptionLayer:
    """Fetches live market signals and detects contradictions between sentiment layers."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._client = httpx.Client(timeout=30.0)
        self._echo_log_path = self.settings.short_term_memory_path.parent / "echo_log.jsonl"

    def close(self) -> None:
        self._client.close()

    def perceive(self) -> MarketSnapshot:
        """Pull latest market signals, score divergence, attach reasoning hash."""
        global_metrics = self._fetch_global_metrics()
        fear_greed = self._fetch_fear_greed()
        altcoin_season = self._fetch_altcoin_season()
        trending = self._fetch_trending()
        derivatives = self._fetch_derivatives_summary()

        social_heat = self._score_social_heat(trending, altcoin_season)
        on_chain_netflow = self._infer_onchain_flow(global_metrics, altcoin_season, trending)

        snapshot = MarketSnapshot(
            fear_greed_index=fear_greed.get("value"),
            btc_dominance=global_metrics.get("btc_dominance"),
            total_market_cap_usd=global_metrics.get("total_market_cap"),
            total_volume_24h_usd=global_metrics.get("total_volume_24h"),
            funding_rate_avg=derivatives.get("funding_rate_avg"),
            open_interest_change_24h_pct=derivatives.get("oi_change_24h_pct"),
            social_heat_score=social_heat,
            news_sentiment=derivatives.get("news_sentiment"),
            on_chain_netflow=on_chain_netflow,
            raw={
                "global_metrics": global_metrics,
                "fear_greed": fear_greed,
                "altcoin_season": altcoin_season,
                "trending": trending,
                "derivatives": derivatives,
                "sources": fear_greed.get("source", "unknown"),
            },
        )
        snapshot.divergences = self._detect_divergences(snapshot)
        snapshot.divergence_score = self._score_divergence(snapshot)
        snapshot.reasoning_hash = self._reasoning_hash(snapshot)
        return snapshot

    def get_market_snapshot(self, snapshot: MarketSnapshot | None = None) -> dict[str, Any]:
        """Dict view for CLI output and quick inspection."""
        snap = snapshot or self.perceive()
        payload = snap.model_dump(mode="json")
        payload["social_heat"] = self._social_heat_label(snap.social_heat_score)
        payload["onchain_flow"] = snap.on_chain_netflow
        return payload

    def save_echo(self, snapshot: MarketSnapshot | dict[str, Any]) -> None:
        """Append a perception echo to the JSONL audit log."""
        if isinstance(snapshot, MarketSnapshot):
            record = snapshot.model_dump(mode="json")
        else:
            record = snapshot

        self._echo_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._echo_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        logger.info("Saved echo to %s", self._echo_log_path)

    def _headers(self) -> dict[str, str]:
        return {
            "X-CMC_PRO_API_KEY": self.settings.cmc_api_key,
            "Accept": "application/json",
        }

    def _fetch_fear_greed(self) -> dict[str, Any]:
        if self.settings.cmc_api_key:
            cmc = self._fetch_cmc_fear_greed()
            if cmc.get("value") is not None:
                return cmc
        return self._fetch_public_fear_greed()

    def _fetch_cmc_fear_greed(self) -> dict[str, Any]:
        try:
            response = self._client.get(
                f"{CMC_REST_BASE}/v3/fear-and-greed/latest",
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()["data"]
            return {
                "value": int(data["value"]),
                "classification": data.get("value_classification", "Unknown"),
                "source": "coinmarketcap",
            }
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            logger.warning("CMC Fear & Greed fetch failed: %s", exc)
            return {"value": None, "classification": None, "source": "coinmarketcap_failed"}

    def _fetch_public_fear_greed(self) -> dict[str, Any]:
        try:
            response = self._client.get(FNG_PUBLIC_URL)
            response.raise_for_status()
            point = response.json()["data"][0]
            return {
                "value": int(point["value"]),
                "classification": point.get("value_classification", "Unknown"),
                "source": "alternative.me",
            }
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            logger.warning("Public Fear & Greed fetch failed: %s", exc)
            return {"value": 50, "classification": "Neutral", "source": "fallback"}

    def _fetch_global_metrics(self) -> dict[str, Any]:
        if not self.settings.cmc_api_key:
            return self._mock_global_metrics()

        try:
            response = self._client.get(
                f"{CMC_REST_BASE}/v1/global-metrics/quotes/latest",
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()["data"]
            quote = data.get("quote", {}).get("USD", {})
            return {
                "btc_dominance": data.get("btc_dominance"),
                "eth_dominance": data.get("eth_dominance"),
                "total_market_cap": quote.get("total_market_cap"),
                "total_volume_24h": quote.get("total_volume_24h"),
                "altcoin_market_cap": quote.get("altcoin_market_cap"),
                "source": "coinmarketcap",
            }
        except (httpx.HTTPError, KeyError, TypeError) as exc:
            logger.warning("Global metrics fetch failed, using mock: %s", exc)
            return self._mock_global_metrics()

    def _fetch_altcoin_season(self) -> dict[str, Any]:
        if not self.settings.cmc_api_key:
            return {"altcoin_index": None, "source": "unavailable"}

        try:
            response = self._client.get(
                f"{CMC_REST_BASE}/v1/altcoin-season-index/latest",
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()["data"]
            return {
                "altcoin_index": data.get("altcoin_index"),
                "snapshot_time": data.get("snapshot_time"),
                "source": "coinmarketcap",
            }
        except (httpx.HTTPError, KeyError, TypeError) as exc:
            logger.warning("Altcoin season fetch failed: %s", exc)
            return {"altcoin_index": None, "source": "unavailable"}

    def _fetch_trending(self) -> dict[str, Any]:
        if not self.settings.cmc_api_key:
            return {"coins": [], "avg_change_24h": None, "source": "unavailable"}

        try:
            response = self._client.get(
                f"{CMC_REST_BASE}/v1/cryptocurrency/trending/latest",
                headers=self._headers(),
            )
            response.raise_for_status()
            coins = response.json().get("data", [])
            changes = [
                float(c.get("quote", {}).get("USD", {}).get("percent_change_24h", 0))
                for c in coins
                if c.get("quote", {}).get("USD", {}).get("percent_change_24h") is not None
            ]
            avg_change = sum(changes) / len(changes) if changes else None
            return {
                "coins": [
                    {
                        "symbol": c.get("symbol"),
                        "name": c.get("name"),
                        "percent_change_24h": c.get("quote", {}).get("USD", {}).get("percent_change_24h"),
                    }
                    for c in coins[:5]
                ],
                "avg_change_24h": avg_change,
                "source": "coinmarketcap",
            }
        except (httpx.HTTPError, KeyError, TypeError) as exc:
            logger.warning("Trending fetch failed: %s", exc)
            return {"coins": [], "avg_change_24h": None, "source": "unavailable"}

    def _fetch_derivatives_summary(self) -> dict[str, Any]:
        """Derivatives via MCP when available; heuristic fallback otherwise."""
        if self.settings.cmc_api_key:
            mcp_data = self._try_mcp_derivatives()
            if mcp_data:
                return mcp_data

        return {
            "funding_rate_avg": None,
            "oi_change_24h_pct": None,
            "news_sentiment": "unavailable_without_cmc_key",
            "source": "stub",
        }

    def _try_mcp_derivatives(self) -> dict[str, Any] | None:
        try:
            result = self.call_mcp_tool("get_derivatives_data", {})
            content = result.get("result", {}).get("content", [])
            if not content:
                return None
            text = content[0].get("text", "{}")
            parsed = json.loads(text) if isinstance(text, str) else text
            return {
                "funding_rate_avg": parsed.get("funding_rate_avg") or parsed.get("funding_rate"),
                "oi_change_24h_pct": parsed.get("open_interest_change_24h"),
                "news_sentiment": parsed.get("sentiment", "mixed"),
                "source": "cmc_mcp",
            }
        except Exception as exc:
            logger.debug("MCP derivatives unavailable: %s", exc)
            return None

    def call_mcp_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.cmc_api_key:
            raise RuntimeError("CMC_API_KEY required for MCP tool calls")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        response = self._client.post(
            self.settings.cmc_mcp_url,
            headers={
                "X-CMC-MCP-API-KEY": self.settings.cmc_api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            content=json.dumps(payload),
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _score_social_heat(trending: dict[str, Any], altcoin_season: dict[str, Any]) -> float:
        score = 0.5
        avg_change = trending.get("avg_change_24h")
        if avg_change is not None:
            if avg_change > 15:
                score = 0.9
            elif avg_change > 8:
                score = 0.75
            elif avg_change < -5:
                score = 0.3

        alt_index = altcoin_season.get("altcoin_index")
        if alt_index is not None:
            if alt_index >= 75:
                score = min(1.0, score + 0.15)
            elif alt_index <= 25:
                score = max(0.0, score - 0.15)

        return round(score, 2)

    @staticmethod
    def _infer_onchain_flow(
        global_metrics: dict[str, Any],
        altcoin_season: dict[str, Any],
        trending: dict[str, Any],
    ) -> str:
        btc_dom = global_metrics.get("btc_dominance")
        alt_index = altcoin_season.get("altcoin_index")
        avg_change = trending.get("avg_change_24h")

        if btc_dom is not None and btc_dom > 60 and avg_change is not None and avg_change < 0:
            return "whale_distribution"

        if alt_index is not None and alt_index >= 70:
            return "alt_rotation"

        if avg_change is not None and avg_change > 10:
            return "retail_inflow"

        return "neutral"

    @staticmethod
    def _social_heat_label(score: float | None) -> str:
        if score is None:
            return "unknown"
        if score >= 0.75:
            return "high"
        if score <= 0.35:
            return "low"
        return "moderate"

    @staticmethod
    def _detect_divergences(snapshot: MarketSnapshot) -> list[str]:
        divergences: list[str] = []
        fg = snapshot.fear_greed_index
        flow = snapshot.on_chain_netflow

        if fg is not None and fg > 70 and flow in ("whale_distribution", "outflow"):
            divergences.append("Extreme greed with whale distribution — euphoria vs exit")

        if fg is not None and fg < 30 and PerceptionLayer._social_heat_label(snapshot.social_heat_score) == "high":
            divergences.append("Fear on index but social heat high — bullish contrarian setup")

        funding = snapshot.funding_rate_avg
        if funding is not None and funding > 0.05 and snapshot.social_heat_score and snapshot.social_heat_score > 0.8:
            divergences.append("Crowded longs with frothy social heat — squeeze risk")

        if snapshot.open_interest_change_24h_pct and snapshot.open_interest_change_24h_pct > 10:
            if fg is not None and fg < 40:
                divergences.append("Rising OI into fear — positioning divergence")

        if fg is not None and fg > 75 and flow == "whale_distribution":
            divergences.append("Strong bearish divergence — hype vs on-chain exit")

        return divergences

    @staticmethod
    def _score_divergence(snapshot: MarketSnapshot) -> str:
        fg = snapshot.fear_greed_index or 50
        heat = PerceptionLayer._social_heat_label(snapshot.social_heat_score)
        flow = snapshot.on_chain_netflow or "neutral"

        if fg > 70 and flow in ("whale_distribution", "outflow"):
            return "strong_bearish_divergence"
        if fg < 30 and heat == "high":
            return "bullish_contrarian"
        if snapshot.divergences:
            return "mixed_signals"
        return "neutral"

    @staticmethod
    def _reasoning_hash(snapshot: MarketSnapshot) -> str:
        payload = snapshot.model_dump(mode="json")
        payload.pop("reasoning_hash", None)
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()
        return digest[:12]

    @staticmethod
    def _mock_global_metrics() -> dict[str, Any]:
        return {
            "btc_dominance": 58.2,
            "eth_dominance": 12.1,
            "total_market_cap": 2_400_000_000_000,
            "total_volume_24h": 95_000_000_000,
            "altcoin_market_cap": 1_000_000_000_000,
            "source": "mock",
        }


# Alias for quick imports
PerceptionAgent = PerceptionLayer