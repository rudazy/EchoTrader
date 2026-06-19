"""Execution layer — TWAK CLI integration for quotes and autonomous swaps."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from agents.twak_client import TwakClient
from agents.types import RiskAssessment, TradeAction, TradeDecision
from config.settings import Settings

logger = logging.getLogger(__name__)


class Executor:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.twak = TwakClient(self.settings)

    def get_swap_quote(
        self,
        from_token: str = "USDT",
        to_token: str = "BNB",
        amount: str | None = None,
        chain: str | None = None,
    ) -> dict[str, Any]:
        """Fetch a TWAK swap quote. Works in dry-run — no wallet password required."""
        result = self.twak.get_swap_quote(from_token, to_token, amount, chain)
        payload: dict[str, Any] = {
            "success": result["success"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount or self.settings.twak_quote_amount,
            "chain": chain or self.settings.twak_chain,
            "dry_run": self.settings.dry_run,
        }
        if result["success"]:
            quote = result["quote"] or {}
            payload["quote"] = quote
            logger.info(
                "TWAK quote: %s -> %s via %s",
                quote.get("input"),
                quote.get("output"),
                quote.get("provider"),
            )
        else:
            payload["error"] = result.get("error")
            payload["error_code"] = result.get("error_code", "UNKNOWN_ERROR")
            logger.warning("TWAK quote failed: %s", payload["error"])
        return payload

    def execute_trade(self, decision: TradeDecision | dict[str, Any]) -> dict[str, Any]:
        """Execute a trade from a reasoner decision or dict. Respects DRY_RUN."""
        if isinstance(decision, dict):
            decision = TradeDecision(
                thesis=decision.get("thesis", ""),
                confidence=float(decision.get("confidence", 0)),
                action=TradeAction(decision.get("action", "hold")),
                token=decision.get("token"),
                direction=decision.get("direction"),
                size_pct=float(decision.get("size_pct", 0)),
                stop_loss_pct=decision.get("stop_loss_pct"),
                reasoning=decision.get("reasoning", ""),
                contradictions=decision.get("contradictions", []),
            )

        from agents.risk_guard import RiskGuard
        from agents.types import MarketSnapshot

        risk = RiskGuard(self.settings).assess(MarketSnapshot(), decision)
        return self.execute(decision, risk)

    def execute(
        self,
        decision: TradeDecision,
        risk: RiskAssessment,
        reasoning_hash: str | None = None,
    ) -> dict[str, Any]:
        """Execute or simulate a trade via TWAK."""
        result: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": decision.action.value,
            "token": decision.token,
            "size_pct": risk.adjusted_size_pct,
            "regime": risk.regime.value,
            "thesis": decision.thesis,
            "reasoning": decision.reasoning,
            "reasoning_hash": reasoning_hash or self._hash_reasoning(decision),
            "executed": False,
            "dry_run": self.settings.dry_run,
        }

        if not risk.approved:
            result["status"] = "blocked"
            result["reasons"] = risk.reasons
            self._log_trade(result)
            return result

        if decision.action in (TradeAction.HOLD, TradeAction.FLAT):
            result["status"] = "skipped"
            self._log_trade(result)
            return result

        if self.settings.twak_enabled and not self.twak.credentials_configured():
            result["status"] = "twak_unconfigured"
            result["error"] = "Set TWAK_ACCESS_ID and TWAK_HMAC_SECRET"
            self._log_trade(result)
            return result

        quote = self._twak_quote(decision, risk)
        result["quote"] = quote

        if quote.get("error") or quote.get("errorCode"):
            result["status"] = "quote_failed"
            result["error"] = quote
            self._log_trade(result)
            return result

        if self.settings.dry_run:
            result["status"] = "dry_run"
            result["message"] = self._format_personality(decision, risk)
            result["quote_summary"] = self._format_quote(quote)
            self._log_trade(result)
            return result

        if not self.twak.wallet_password_configured():
            result["status"] = "wallet_password_missing"
            result["error"] = "TWAK_WALLET_PASSWORD required for live swaps"
            self._log_trade(result)
            return result

        swap = self._twak_swap(decision, risk)
        result["swap"] = swap
        result["executed"] = "error" not in swap and "errorCode" not in swap
        result["status"] = "executed" if result["executed"] else "failed"
        result["message"] = self._format_personality(decision, risk)
        if result["executed"]:
            result["tx_hash"] = swap.get("hash")
            result["explorer"] = swap.get("explorer")
            result["quote_summary"] = self._format_quote(quote)
        self._log_trade(result)
        return result

    def _twak_quote(self, decision: TradeDecision, risk: RiskAssessment) -> dict[str, Any]:
        from_token, to_token = self._resolve_pair(decision)
        result = self.get_swap_quote(
            from_token=from_token,
            to_token=to_token,
            amount=self.settings.twak_quote_amount,
            chain=self.settings.twak_chain,
        )
        if result.get("success"):
            return result["quote"]
        return {
            "error": result.get("error"),
            "errorCode": result.get("error_code", "UNKNOWN_ERROR"),
        }

    def _twak_swap(self, decision: TradeDecision, risk: RiskAssessment) -> dict[str, Any]:
        from_token, to_token = self._resolve_pair(decision)
        return self.twak.execute_swap(
            from_token=from_token,
            to_token=to_token,
            amount=self.settings.twak_quote_amount,
            chain=self.settings.twak_chain,
        )

    def _resolve_pair(self, decision: TradeDecision) -> tuple[str, str]:
        token = (decision.token or "BNB").upper()
        if decision.action == TradeAction.BUY:
            return "USDT", token
        if decision.action in (TradeAction.SELL, TradeAction.SHORT):
            return token, "USDT"
        return "USDT", token

    @staticmethod
    def _format_quote(quote: dict[str, Any]) -> str:
        if quote.get("raw"):
            return str(quote.get("output", quote.get("quote", quote)))
        parts = [
            quote.get("input"),
            "->",
            quote.get("output"),
            f"({quote.get('provider', 'unknown')})",
        ]
        if quote.get("priceImpact"):
            parts.append(f"impact {quote['priceImpact']}")
        return " ".join(str(p) for p in parts if p)

    def _hash_reasoning(self, decision: TradeDecision) -> str:
        payload = f"{decision.thesis}|{decision.reasoning}|{decision.action.value}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _format_personality(self, decision: TradeDecision, risk: RiskAssessment) -> str:
        contradictions = ", ".join(decision.contradictions[:2]) or "no major tension"
        return (
            f"{decision.reasoning} "
            f"[{risk.regime.value}] contradictions: {contradictions} "
            f"-> {decision.action.value} {decision.token or ''} "
            f"at {risk.adjusted_size_pct:.1f}% size"
        ).strip()

    def _log_trade(self, entry: dict[str, Any]) -> None:
        path = self.settings.trades_log_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
        logger.info("Trade log: %s", entry.get("status", "logged"))


ExecutorAgent = Executor