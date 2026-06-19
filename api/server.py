"""FastAPI dashboard API — serves live agent state to the Next.js frontend."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.perception import PerceptionLayer
from agents.reasoner import Reasoner
from agents.risk_guard import RiskGuard
from config.settings import get_settings

app = FastAPI(title="EchoTrader API", version="0.1.0")

_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://echotrader.vercel.app",
]
_extra_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[*_default_origins, *_extra_origins],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _read_jsonl(path: Path, limit: int = 20) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _read_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _fear_label(value: int | None) -> str:
    if value is None:
        return "UNKNOWN"
    if value <= 25:
        return "EXTREME FEAR"
    if value <= 45:
        return "FEAR"
    if value <= 55:
        return "NEUTRAL"
    if value <= 75:
        return "GREED"
    return "EXTREME GREED"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/status")
def status(refresh: bool = False) -> dict[str, Any]:
    """Return dashboard payload. Set refresh=true to run a live perception+reason cycle."""
    settings = get_settings()
    echoes = _read_jsonl(settings.short_term_memory_path.parent / "echo_log.jsonl", limit=1)
    perception = echoes[-1] if echoes else None

    reasoner_payload: dict[str, Any] | None = None
    decision_payload: dict[str, Any] | None = None
    risk_payload: dict[str, Any] | None = None
    regime = "unknown"

    if refresh or perception is None:
        layer = PerceptionLayer(settings)
        try:
            snapshot = layer.perceive()
            layer.save_echo(snapshot)
            perception = layer.get_market_snapshot(snapshot)
            thinking = Reasoner(settings).think(snapshot)
            decision = thinking["decision"]
            risk = RiskGuard(settings).assess(snapshot, decision)
            reasoner_payload = {
                "market_read": thinking["market_read"],
                "risk_notes": thinking["risk_notes"],
                "confidence_pct": thinking["confidence_pct"],
                "reasoning": decision.reasoning,
                "reasoning_hash": thinking["reasoning_hash"],
            }
            decision_payload = decision.model_dump(mode="json")
            risk_payload = {
                "approved": risk.approved,
                "regime": risk.regime.value,
                "adjusted_size_pct": risk.adjusted_size_pct,
                "reasons": risk.reasons,
            }
            regime = risk.regime.value
        finally:
            layer.close()
    else:
        fg = perception.get("fear_greed_index")
        if fg is not None and fg <= 30:
            regime = "trending_bear"
        trade_echoes = _read_json_array(settings.short_term_memory_path)
        if trade_echoes:
            latest = trade_echoes[-1]
            decision_payload = {
                "action": latest.get("action"),
                "token": "BNB",
                "confidence": latest.get("confidence"),
                "size_pct": 2.0,
                "thesis": latest.get("thesis"),
            }
            reasoner_payload = {
                "market_read": (
                    f"Fear & Greed at {fg} — blood in the streets, but that's where "
                    "measured entries print if you're not reckless."
                ),
                "risk_notes": "Hard stop 3% below entry. Bail if bounce fails on volume.",
                "confidence_pct": int((latest.get("confidence") or 0.65) * 100),
                "reasoning_hash": perception.get("reasoning_hash"),
            }

    trades = _read_jsonl(settings.trades_log_path, limit=10)
    trade_echoes = _read_json_array(settings.short_term_memory_path)[-8:]
    perception_history = _read_jsonl(
        settings.short_term_memory_path.parent / "echo_log.jsonl",
        limit=12,
    )
    history_payload = [
        {
            "timestamp": entry.get("timestamp"),
            "fear_greed_index": entry.get("fear_greed_index"),
            "divergence_score": entry.get("divergence_score"),
            "reasoning_hash": entry.get("reasoning_hash"),
        }
        for entry in perception_history
    ]

    fg_value = (perception or {}).get("fear_greed_index")
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_online": True,
        "dry_run": settings.dry_run,
        "chain": settings.twak_chain.upper(),
        "regime_label": _fear_label(fg_value),
        "regime": regime,
        "perception": perception,
        "reasoner": reasoner_payload,
        "decision": decision_payload,
        "risk": risk_payload,
        "signals": {
            "fear_greed": fg_value,
            "fear_greed_label": (perception or {}).get("raw", {}).get("fear_greed", {}).get("classification"),
            "divergence_score": (perception or {}).get("divergence_score"),
            "btc_dominance": (perception or {}).get("btc_dominance"),
            "social_heat": (perception or {}).get("social_heat_score"),
            "onchain_flow": (perception or {}).get("on_chain_netflow"),
        },
        "perception_history": history_payload,
        "recent_trades": list(reversed(trades)),
        "recent_echoes": list(reversed(trade_echoes)),
        "portfolio": {
            "allocated_capital_usd": 1000,
            "deployed_pct": decision_payload.get("size_pct", 0) if decision_payload else 0,
            "token": (decision_payload or {}).get("token", "BNB"),
            "network": settings.twak_chain,
        },
    }


def main() -> None:
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()