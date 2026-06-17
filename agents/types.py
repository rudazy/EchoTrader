from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MarketRegime(str, Enum):
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    CHOPPY = "choppy"
    HIGH_VOL = "high_vol"
    SQUEEZE_SETUP = "squeeze_setup"
    UNKNOWN = "unknown"


class TradeAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"
    HOLD = "hold"
    FLAT = "flat"


class MarketSnapshot(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fear_greed_index: int | None = None
    btc_dominance: float | None = None
    total_market_cap_usd: float | None = None
    total_volume_24h_usd: float | None = None
    funding_rate_avg: float | None = None
    open_interest_change_24h_pct: float | None = None
    social_heat_score: float | None = None
    news_sentiment: str | None = None
    on_chain_netflow: str | None = None
    divergences: list[str] = Field(default_factory=list)
    divergence_score: str = "neutral"
    reasoning_hash: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class TradeDecision(BaseModel):
    thesis: str
    confidence: float = Field(ge=0.0, le=1.0)
    action: TradeAction
    token: str | None = None
    direction: str | None = None
    size_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    stop_loss_pct: float | None = None
    reasoning: str = ""
    market_read: str = ""
    risk_notes: str = ""
    contradictions: list[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    approved: bool
    regime: MarketRegime
    adjusted_size_pct: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    cooldown_active: bool = False


class EchoRecord(BaseModel):
    id: str
    timestamp: datetime
    snapshot_summary: str
    thesis: str
    action: TradeAction
    confidence: float
    outcome: str | None = None
    pnl_pct: float | None = None