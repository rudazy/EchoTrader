"""Execution layer — TWAK CLI integration for quotes and autonomous swaps."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from typing import Any

from agents.types import RiskAssessment, TradeAction, TradeDecision
from config.settings import Settings

logger = logging.getLogger(__name__)

TWAK_TIMEOUT_SECONDS = 30


class Executor:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def get_swap_quote(
        self,
        from_token: str = "USDT",
        to_token: str = "BNB",
        amount: str | None = None,
        chain: str | None = None,
    ) -> dict[str, Any]:
        """Fetch a TWAK swap quote. Works in dry-run — no wallet password required."""
        amount = amount or self.settings.twak_quote_amount
        chain = chain or self.settings.twak_chain
        cmd = [
            "twak",
            "swap",
            amount,
            from_token,
            to_token,
            "--chain",
            chain,
            "--slippage",
            str(self.settings.default_slippage_pct),
            "--quote-only",
            "--json",
        ]
        quote = self._run_twak(cmd)
        success = "error" not in quote and "errorCode" not in quote
        result: dict[str, Any] = {
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount,
            "chain": chain,
            "dry_run": self.settings.dry_run,
        }
        if success:
            result["quote"] = quote
            logger.info(
                "TWAK quote: %s -> %s via %s",
                quote.get("input"),
                quote.get("output"),
                quote.get("provider"),
            )
        else:
            result["error"] = quote.get("error", quote)
            result["error_code"] = quote.get("errorCode", "UNKNOWN_ERROR")
            logger.warning("TWAK quote failed: %s", result["error"])
        return result

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

        swap = self._twak_swap(decision, risk)
        result["swap"] = swap
        result["executed"] = "error" not in swap and "errorCode" not in swap
        result["status"] = "executed" if result["executed"] else "failed"
        result["message"] = self._format_personality(decision, risk)
        if result["executed"]:
            result["tx_hash"] = swap.get("hash")
            result["explorer"] = swap.get("explorer")
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
        cmd = [
            "twak",
            "swap",
            self.settings.twak_quote_amount,
            from_token,
            to_token,
            "--chain",
            self.settings.twak_chain,
            "--slippage",
            str(self.settings.default_slippage_pct),
            "--json",
        ]
        return self._run_twak(cmd)

    def _run_twak(self, cmd: list[str]) -> dict[str, Any]:
        env = os.environ.copy()
        if self.settings.twak_access_id:
            env["TWAK_ACCESS_ID"] = self.settings.twak_access_id
        if self.settings.twak_hmac_secret:
            env["TWAK_HMAC_SECRET"] = self.settings.twak_hmac_secret
        if self.settings.twak_wallet_password:
            env["TWAK_WALLET_PASSWORD"] = self.settings.twak_wallet_password

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=TWAK_TIMEOUT_SECONDS,
                env=env,
            )
            stdout = proc.stdout.strip()
            if stdout:
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError:
                    return {"quote": stdout, "raw": True}
            stderr = proc.stderr.strip() or "empty stdout"
            return {"error": stderr, "errorCode": "UNKNOWN_ERROR", "returncode": proc.returncode}
        except FileNotFoundError:
            return {
                "error": "twak CLI not found — install via https://agent-kit.trustwallet.com/",
                "errorCode": "CLI_NOT_FOUND",
            }
        except subprocess.TimeoutExpired:
            return {"error": "TWAK command timed out", "errorCode": "TIMEOUT"}
        except json.JSONDecodeError as exc:
            return {"error": str(exc), "errorCode": "PARSE_ERROR"}

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
            return str(quote.get("quote", quote))
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