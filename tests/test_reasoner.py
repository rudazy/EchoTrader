import json

from agents.reasoner import Reasoner, ReasonerAgent
from agents.types import MarketSnapshot, TradeAction
from config.settings import Settings


def test_parse_decision_from_json_block():
    reasoner = Reasoner(Settings(anthropic_api_key="test", cmc_api_key="test"))
    raw = """```json
{
  "market_read": "Blood in the streets, but I'm not a hero.",
  "thesis": "Market is conflicted",
  "confidence": 0.72,
  "action": "hold",
  "token": null,
  "direction": null,
  "size_pct": 0,
  "stop_loss_pct": null,
  "reasoning": "Social frothy but whales exiting.",
  "risk_notes": "Wait for clarity.",
  "contradictions": ["hype vs flow"]
}
```"""
    decision = reasoner._parse_decision(raw)
    assert decision.action == TradeAction.HOLD
    assert decision.confidence == 0.72
    assert decision.market_read.startswith("Blood")
    assert decision.risk_notes == "Wait for clarity."


def test_parse_confidence_percent_scale():
    reasoner = Reasoner(Settings(anthropic_api_key="test", cmc_api_key="test"))
    raw = json.dumps({
        "market_read": "test",
        "thesis": "test",
        "confidence": 65,
        "action": "buy",
        "token": "BNB",
        "size_pct": 2.0,
        "reasoning": "go",
        "risk_notes": "tight stop",
    })
    decision = reasoner._parse_decision(raw)
    assert decision.confidence == 0.65


def test_fallback_think_extreme_fear():
    reasoner = Reasoner(Settings(cmc_api_key="test"))
    snapshot = MarketSnapshot(fear_greed_index=22, divergence_score="neutral")
    result = reasoner.think(snapshot)
    assert result["decision"].action == TradeAction.BUY
    assert "22" in result["market_read"]
    assert result["confidence_pct"] == 65


def test_format_thinking_output():
    reasoner = Reasoner(Settings(cmc_api_key="test"))
    snapshot = MarketSnapshot(fear_greed_index=22)
    result = reasoner.think(snapshot)
    formatted = reasoner.format_thinking(result)
    assert "EchoTrader thinking:" in formatted
    assert "Risk:" in formatted
    assert "Confidence: 65%" in formatted


def test_reasoner_agent_alias():
    assert ReasonerAgent is Reasoner