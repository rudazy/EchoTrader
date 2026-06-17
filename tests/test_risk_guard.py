from agents.risk_guard import RiskGuard
from agents.types import MarketRegime, MarketSnapshot, TradeAction, TradeDecision
from config.settings import Settings


def make_settings(**overrides) -> Settings:
    base = {
        "anthropic_api_key": "test",
        "cmc_api_key": "test",
        "dry_run": True,
        "max_daily_drawdown_pct": 3.0,
        "max_position_size_pct": 5.0,
        "cooldown_minutes": 60,
        "token_allowlist": "BNB,ETH,USDT",
    }
    base.update(overrides)
    return Settings(**base)


def test_blocks_unlisted_token():
    guard = RiskGuard(make_settings())
    snapshot = MarketSnapshot(fear_greed_index=50)
    decision = TradeDecision(
        thesis="test",
        confidence=0.8,
        action=TradeAction.BUY,
        token="DOGE",
        size_pct=3.0,
    )
    risk = guard.assess(snapshot, decision)
    assert risk.approved is False
    assert any("allowlist" in r for r in risk.reasons)


def test_blocks_low_confidence():
    guard = RiskGuard(make_settings())
    snapshot = MarketSnapshot(fear_greed_index=50)
    decision = TradeDecision(
        thesis="test",
        confidence=0.4,
        action=TradeAction.BUY,
        token="BNB",
        size_pct=3.0,
    )
    risk = guard.assess(snapshot, decision)
    assert risk.approved is False


def test_classifies_squeeze_regime():
    guard = RiskGuard(make_settings())
    snapshot = MarketSnapshot(
        fear_greed_index=70,
        funding_rate_avg=0.06,
        open_interest_change_24h_pct=12.0,
    )
    regime = guard._classify_regime(snapshot)
    assert regime == MarketRegime.SQUEEZE_SETUP


def test_reduces_size_in_high_vol():
    guard = RiskGuard(make_settings())
    snapshot = MarketSnapshot(
        fear_greed_index=90,
        open_interest_change_24h_pct=20.0,
    )
    decision = TradeDecision(
        thesis="test",
        confidence=0.75,
        action=TradeAction.BUY,
        token="BNB",
        size_pct=4.0,
    )
    risk = guard.assess(snapshot, decision)
    assert risk.adjusted_size_pct == 2.0


def test_hold_always_approved():
    guard = RiskGuard(make_settings())
    snapshot = MarketSnapshot()
    decision = TradeDecision(
        thesis="sit tight",
        confidence=0.9,
        action=TradeAction.HOLD,
        size_pct=0.0,
    )
    risk = guard.assess(snapshot, decision)
    assert risk.approved is True
    assert risk.adjusted_size_pct == 0.0