"""Run N demo dry-run trades — seeds trades.log and short_term memory for the dashboard."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.executor import Executor
from agents.types import EchoRecord, MarketRegime, MarketSnapshot, RiskAssessment, TradeAction, TradeDecision
from config.settings import get_settings

DEMO_TRADES: list[dict] = [
    {
        "token": "BNB",
        "action": TradeAction.BUY,
        "size_pct": 3.0,
        "confidence": 0.68,
        "thesis": "Extreme fear contrarian probe — small size, tight stop",
        "reasoning": "FG sub-25 with stable BTC dominance — measured dip buy.",
    },
    {
        "token": "ETH",
        "action": TradeAction.BUY,
        "size_pct": 2.5,
        "confidence": 0.62,
        "thesis": "ETH lagging BNB in fear regime — relative value entry",
        "reasoning": "Altcoin index neutral; ETH/BNB spread widened on flush.",
    },
    {
        "token": "BNB",
        "action": TradeAction.SELL,
        "size_pct": 2.0,
        "confidence": 0.71,
        "thesis": "Trim into dead-cat bounce — no volume confirmation",
        "reasoning": "Short-term relief rally without OI expansion; take profit.",
    },
    {
        "token": "USDT",
        "action": TradeAction.BUY,
        "size_pct": 1.5,
        "confidence": 0.58,
        "thesis": "Raise cash buffer ahead of macro event window",
        "reasoning": "Risk-off staging; reduce net exposure before volatility.",
    },
    {
        "token": "BNB",
        "action": TradeAction.BUY,
        "size_pct": 4.0,
        "confidence": 0.74,
        "thesis": "Second tranche on confirmed support hold",
        "reasoning": "Prior probe held; add with hard stop below sweep low.",
    },
]


def _append_echo(settings, decision: TradeDecision, fg: int = 20) -> None:
    path = settings.short_term_memory_path
    path.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    if path.exists():
        records = json.loads(path.read_text(encoding="utf-8"))
    records.append(
        EchoRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            snapshot_summary=f"FG={fg}, divs=0",
            thesis=decision.thesis,
            action=decision.action,
            confidence=decision.confidence,
        ).model_dump(mode="json")
    )
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def run_demo_trades(count: int = 5) -> list[dict]:
    settings = get_settings()
    issues = settings.validate_twak()
    if issues:
        raise RuntimeError(
            "TWAK not configured. Set TWAK_ACCESS_ID and TWAK_HMAC_SECRET in .env. "
            f"Missing: {', '.join(issues)}"
        )

    executor = Executor(settings)
    results: list[dict] = []

    for spec in DEMO_TRADES[:count]:
        decision = TradeDecision(
            thesis=spec["thesis"],
            confidence=spec["confidence"],
            action=spec["action"],
            token=spec["token"],
            size_pct=spec["size_pct"],
            reasoning=spec["reasoning"],
        )
        risk = RiskAssessment(
            approved=True,
            regime=MarketRegime.TRENDING_BEAR,
            adjusted_size_pct=spec["size_pct"],
        )
        result = executor.execute(decision, risk, reasoning_hash=f"demo-{uuid.uuid4().hex[:8]}")
        _append_echo(settings, decision)
        results.append(result)
        print(
            f"[{result['status']}] {result['action'].upper()} {result['token']} "
            f"@ {result['size_pct']}% — {result.get('quote_summary', result.get('error', 'no quote'))}"
        )

    print(f"\nLogged {len(results)} trades to {settings.trades_log_path}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run demo trades via live TWAK quotes")
    parser.add_argument("-n", "--count", type=int, default=5, help="Number of trades (max 5)")
    args = parser.parse_args()
    count = max(1, min(args.count, len(DEMO_TRADES)))
    run_demo_trades(count)


if __name__ == "__main__":
    main()