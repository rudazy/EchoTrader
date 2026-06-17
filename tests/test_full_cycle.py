from agents.types import TradeAction
from main import _should_quote


def test_should_quote_on_extreme_fear():
    assert _should_quote({"fear_greed_index": 22, "divergence_score": "neutral"}) is True


def test_should_quote_on_divergence():
    assert _should_quote({"fear_greed_index": 50, "divergence_score": "bullish_contrarian"}) is True


def test_should_not_quote_on_neutral():
    assert _should_quote({"fear_greed_index": 50, "divergence_score": "neutral"}) is False


def test_reasoner_fallback_buys_in_extreme_fear():
    from agents.reasoner import ReasonerAgent
    from agents.types import MarketSnapshot
    from config.settings import Settings

    reasoner = ReasonerAgent(Settings(cmc_api_key="x"))
    decision = reasoner.think(MarketSnapshot(fear_greed_index=22, divergence_score="neutral"))["decision"]
    assert decision.action == TradeAction.BUY
    assert decision.token == "BNB"