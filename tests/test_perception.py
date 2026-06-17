from agents.perception import PerceptionAgent, PerceptionLayer
from agents.types import MarketSnapshot
from config.settings import Settings


def test_detects_greed_outflow_divergence():
    snapshot = MarketSnapshot(
        fear_greed_index=80,
        on_chain_netflow="whale_distribution",
    )
    divergences = PerceptionLayer._detect_divergences(snapshot)
    assert len(divergences) >= 1
    assert any("greed" in d.lower() or "bearish" in d.lower() for d in divergences)


def test_detects_bullish_contrarian():
    snapshot = MarketSnapshot(
        fear_greed_index=25,
        social_heat_score=0.85,
    )
    score = PerceptionLayer._score_divergence(snapshot)
    assert score == "bullish_contrarian"


def test_detects_crowded_longs():
    snapshot = MarketSnapshot(
        funding_rate_avg=0.06,
        social_heat_score=0.9,
    )
    divergences = PerceptionLayer._detect_divergences(snapshot)
    assert any("crowded" in d.lower() for d in divergences)


def test_strong_bearish_divergence_score():
    snapshot = MarketSnapshot(
        fear_greed_index=75,
        on_chain_netflow="whale_distribution",
    )
    snapshot.divergences = PerceptionLayer._detect_divergences(snapshot)
    assert PerceptionLayer._score_divergence(snapshot) == "strong_bearish_divergence"


def test_perceive_without_api_key_uses_live_or_mock():
    settings = Settings(anthropic_api_key="x", cmc_api_key="")
    layer = PerceptionLayer(settings)
    try:
        snapshot = layer.perceive()
        assert snapshot.fear_greed_index is not None
        assert snapshot.reasoning_hash is not None
        assert len(snapshot.reasoning_hash) == 12
        assert snapshot.divergence_score in {
            "neutral",
            "bullish_contrarian",
            "strong_bearish_divergence",
            "mixed_signals",
        }
    finally:
        layer.close()


def test_perception_agent_alias():
    assert PerceptionAgent is PerceptionLayer


def test_reasoning_hash_is_stable():
    snapshot = MarketSnapshot(fear_greed_index=50, divergence_score="neutral")
    h1 = PerceptionLayer._reasoning_hash(snapshot)
    h2 = PerceptionLayer._reasoning_hash(snapshot)
    assert h1 == h2
    assert len(h1) == 12