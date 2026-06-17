"""Risk and regime gatekeeper — hard guardrails before execution."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agents.types import (
    MarketRegime,
    MarketSnapshot,
    RiskAssessment,
    TradeAction,
    TradeDecision,
)
from config.settings import Settings


class RiskGuard:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def assess(
        self,
        snapshot: MarketSnapshot,
        decision: TradeDecision,
        daily_pnl_pct: float = 0.0,
    ) -> RiskAssessment:
        regime = self._classify_regime(snapshot)
        reasons: list[str] = []
        approved = True
        size_pct = decision.size_pct

        if decision.action in (TradeAction.HOLD, TradeAction.FLAT):
            return RiskAssessment(
                approved=True,
                regime=regime,
                adjusted_size_pct=0.0,
                reasons=["No trade requested"],
            )

        if decision.token and decision.token.upper() not in self.settings.allowed_tokens:
            approved = False
            reasons.append(f"Token {decision.token} not on allowlist")

        if decision.confidence < 0.55:
            approved = False
            reasons.append(f"Confidence {decision.confidence:.2f} below 0.55 threshold")

        if daily_pnl_pct <= -self.settings.max_daily_drawdown_pct:
            approved = False
            reasons.append(
                f"Daily drawdown {daily_pnl_pct:.2f}% exceeds "
                f"-{self.settings.max_daily_drawdown_pct}% limit"
            )

        if self._cooldown_active():
            approved = False
            reasons.append(f"Cooldown active ({self.settings.cooldown_minutes}m)")

        if regime == MarketRegime.HIGH_VOL:
            size_pct *= 0.5
            reasons.append("High-vol regime — size halved")

        if regime == MarketRegime.CHOPPY:
            size_pct *= 0.6
            reasons.append("Choppy regime — size reduced 40%")

        if regime == MarketRegime.SQUEEZE_SETUP and decision.action == TradeAction.SHORT:
            size_pct *= 0.7
            reasons.append("Squeeze setup — short size reduced")

        size_pct = min(size_pct, self.settings.max_position_size_pct)

        if size_pct <= 0 and approved:
            approved = False
            reasons.append("Adjusted size is zero")

        return RiskAssessment(
            approved=approved,
            regime=regime,
            adjusted_size_pct=round(size_pct, 4),
            reasons=reasons,
            cooldown_active=self._cooldown_active(),
        )

    def _classify_regime(self, snapshot: MarketSnapshot) -> MarketRegime:
        fg = snapshot.fear_greed_index
        funding = snapshot.funding_rate_avg or 0.0
        oi_change = snapshot.open_interest_change_24h_pct or 0.0

        if funding > 0.04 and oi_change > 8:
            return MarketRegime.SQUEEZE_SETUP

        if abs(oi_change) > 15 or (fg is not None and (fg > 85 or fg < 15)):
            return MarketRegime.HIGH_VOL

        if fg is not None:
            if fg >= 60 and snapshot.btc_dominance and snapshot.btc_dominance < 55:
                return MarketRegime.TRENDING_BULL
            if fg <= 35:
                return MarketRegime.TRENDING_BEAR

        if snapshot.divergences:
            return MarketRegime.CHOPPY

        return MarketRegime.UNKNOWN

    def _cooldown_active(self) -> bool:
        log_path = self.settings.trades_log_path
        if not log_path.exists():
            return False

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.settings.cooldown_minutes)
        for line in reversed(log_path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["timestamp"])
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if entry.get("executed") and ts >= cutoff:
                    return True
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        return False