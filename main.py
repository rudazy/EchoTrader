"""EchoTrader orchestrator — perceive, reason, gate, execute."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time

from agents.executor import Executor, ExecutorAgent
from agents.perception import PerceptionAgent, PerceptionLayer
from agents.reasoner import Reasoner, ReasonerAgent
from agents.risk_guard import RiskGuard
from config.settings import get_settings


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _should_quote(snapshot: dict) -> bool:
    """Quote when divergence fires or sentiment is at an extreme."""
    fg = snapshot.get("fear_greed_index")
    if snapshot.get("divergence_score") != "neutral":
        return True
    if fg is not None and (fg <= 30 or fg >= 70):
        return True
    return False


def run_perception_only() -> dict:
    """Sprint A: live perception cycle without LLM or execution."""
    settings = get_settings()
    perception = PerceptionLayer(settings)
    try:
        snapshot = perception.perceive()
        perception.save_echo(snapshot)
        payload = perception.get_market_snapshot(snapshot)
        print(json.dumps(payload, indent=2, default=str))
        logging.info(
            "Perception complete — FG=%s, divergence=%s, hash=%s",
            snapshot.fear_greed_index,
            snapshot.divergence_score,
            snapshot.reasoning_hash,
        )
        return payload
    finally:
        perception.close()


def run_full_cycle() -> dict:
    """Full demo cycle: perception -> reasoner -> TWAK quote (dry-run safe)."""
    settings = get_settings()
    perception = PerceptionAgent(settings)
    reasoner = ReasonerAgent(settings)
    executor = ExecutorAgent(settings)

    print("EchoTrader full dry cycle")
    try:
        snapshot_obj = perception.perceive()
        perception.save_echo(snapshot_obj)
        snapshot = perception.get_market_snapshot(snapshot_obj)
        print("\n--- Perception ---")
        print(json.dumps(snapshot, indent=2, default=str))

        thinking = reasoner.think(snapshot_obj)
        decision = thinking["decision"]
        print(f"\n--- Reasoner ---\n{reasoner.format_thinking(thinking)}\n")
        print(decision.reasoning)

        cycle_result: dict = {
            "perception": snapshot,
            "thinking": {
                "market_read": thinking["market_read"],
                "risk_notes": thinking["risk_notes"],
                "confidence_pct": thinking["confidence_pct"],
                "reasoning_hash": thinking["reasoning_hash"],
            },
            "decision": decision.model_dump(mode="json"),
            "quote": None,
            "execution": None,
        }

        if decision.action.value in ("hold", "flat") or not _should_quote(snapshot):
            print("\nSitting tight or no actionable signal — cycle complete without quote.")
            cycle_result["status"] = "no_trade"
            return cycle_result

        quote_result = executor.get_swap_quote(
            from_token="USDT",
            to_token=decision.token or "BNB",
            amount=settings.twak_quote_amount,
            chain=settings.twak_chain,
        )
        cycle_result["quote"] = quote_result

        print("--- TWAK Quote ---")
        print(json.dumps(quote_result, indent=2, default=str))

        if quote_result.get("success"):
            execution = executor.execute_trade(decision)
            cycle_result["execution"] = execution
            print("\n--- Execution ---")
            print(json.dumps(execution, indent=2, default=str))
            if execution.get("quote_summary"):
                print(f"\nQuote summary: {execution['quote_summary']}")
        else:
            cycle_result["status"] = "quote_failed"
            print("\nQuote failed — check TWAK install and credentials.")
            print("Install: curl -fsSL https://agent-kit.trustwallet.com/install.sh | bash")

        cycle_result["status"] = cycle_result.get("status", "complete")
        print("\nCycle complete.")
        return cycle_result
    finally:
        perception.close()


def run_cycle(
    daily_pnl_pct: float = 0.0,
    perception_only: bool = False,
    full_cycle: bool = False,
) -> None:
    if full_cycle:
        run_full_cycle()
        return

    if perception_only:
        run_perception_only()
        return

    settings = get_settings()
    settings.validate_runtime()

    perception = PerceptionLayer(settings)
    reasoner = Reasoner(settings)
    risk_guard = RiskGuard(settings)
    executor = Executor(settings)

    try:
        snapshot = perception.perceive()
        perception.save_echo(snapshot)
        logging.info(
            "Perceived market — FG=%s, divergence=%s, signals=%d",
            snapshot.fear_greed_index,
            snapshot.divergence_score,
            len(snapshot.divergences),
        )

        decision = reasoner.reason(snapshot)
        logging.info(
            "Decision: %s %s (confidence=%.2f)",
            decision.action.value,
            decision.token or "",
            decision.confidence,
        )
        print(f"\n{decision.reasoning}\n")

        risk = risk_guard.assess(snapshot, decision, daily_pnl_pct=daily_pnl_pct)
        if not risk.approved:
            logging.warning("Risk blocked: %s", "; ".join(risk.reasons))

        result = executor.execute(decision, risk, reasoning_hash=snapshot.reasoning_hash)
        logging.info("Execution status: %s", result.get("status"))
        if result.get("message"):
            print(result["message"])
        if result.get("quote_summary"):
            print(f"Quote: {result['quote_summary']}")
    finally:
        perception.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="EchoTrader — reflexive market mirror agent")
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    parser.add_argument(
        "--perception-only",
        action="store_true",
        help="Fetch live market snapshot only (no LLM, no execution)",
    )
    parser.add_argument(
        "--full-cycle",
        action="store_true",
        help="Perception + reasoner + TWAK quote (uses Claude if keyed, fallback otherwise)",
    )
    parser.add_argument(
        "--daily-pnl-pct",
        type=float,
        default=0.0,
        help="Simulated daily PnL %% for drawdown guard testing",
    )
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    if args.once or args.perception_only or args.full_cycle:
        run_cycle(
            daily_pnl_pct=args.daily_pnl_pct,
            perception_only=args.perception_only,
            full_cycle=args.full_cycle,
        )
        return

    logging.info(
        "Starting EchoTrader loop (interval=%ds, dry_run=%s)",
        settings.loop_interval_seconds,
        settings.dry_run,
    )
    while True:
        try:
            run_cycle(daily_pnl_pct=args.daily_pnl_pct)
        except KeyboardInterrupt:
            logging.info("Shutting down")
            sys.exit(0)
        except Exception:
            logging.exception("Cycle failed")
        time.sleep(settings.loop_interval_seconds)


if __name__ == "__main__":
    main()