import json
from unittest.mock import MagicMock, patch

from agents.executor import Executor, ExecutorAgent
from agents.types import MarketRegime, RiskAssessment, TradeAction, TradeDecision
from config.settings import Settings


def make_executor(**overrides) -> Executor:
    base = {
        "anthropic_api_key": "x",
        "cmc_api_key": "x",
        "twak_access_id": "access",
        "twak_hmac_secret": "secret",
        "dry_run": True,
        "twak_quote_amount": "10",
        "twak_chain": "bsc",
    }
    base.update(overrides)
    return Executor(Settings(**base))


def test_executor_agent_alias():
    assert ExecutorAgent is Executor


@patch("agents.twak_client.subprocess.run")
def test_get_swap_quote_success(mock_run: MagicMock):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "input": "10.0 USDT",
            "output": "0.015 BNB",
            "provider": "1inch",
            "priceImpact": "0.12%",
        }),
        stderr="",
    )
    executor = make_executor()
    result = executor.get_swap_quote("USDT", "BNB", "10")
    assert result["success"] is True
    assert result["quote"]["output"] == "0.015 BNB"


@patch("agents.twak_client.subprocess.run")
def test_get_swap_quote_cli_not_found(mock_run: MagicMock):
    mock_run.side_effect = FileNotFoundError()
    executor = make_executor()
    result = executor.get_swap_quote()
    assert result["success"] is False
    assert result["error_code"] == "CLI_NOT_FOUND"


@patch("agents.twak_client.subprocess.run")
def test_dry_run_fetches_quote_without_swap(mock_run: MagicMock):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "input": "10.0 USDT",
            "output": "0.015 BNB",
            "provider": "1inch",
        }),
        stderr="",
    )
    executor = make_executor(dry_run=True)
    decision = TradeDecision(
        thesis="test",
        confidence=0.7,
        action=TradeAction.BUY,
        token="BNB",
        size_pct=2.0,
        reasoning="Small probe in fear.",
    )
    risk = RiskAssessment(
        approved=True,
        regime=MarketRegime.TRENDING_BEAR,
        adjusted_size_pct=2.0,
    )
    result = executor.execute(decision, risk)
    assert result["status"] == "dry_run"
    assert result["quote"]["output"] == "0.015 BNB"
    assert mock_run.call_count == 1
    assert "--quote-only" in mock_run.call_args[0][0]


@patch("agents.twak_client.subprocess.run")
def test_live_execution_calls_swap(mock_run: MagicMock):
    quote_json = json.dumps({"input": "10.0 USDT", "output": "0.015 BNB", "provider": "1inch"})
    swap_json = json.dumps({
        "hash": "0xabc",
        "explorer": "https://bscscan.com/tx/0xabc",
        "input": "10.0 USDT",
        "output": "0.015 BNB",
    })
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=quote_json, stderr=""),
        MagicMock(returncode=0, stdout=swap_json, stderr=""),
    ]
    executor = make_executor(dry_run=False, twak_wallet_password="TestPass1")
    decision = TradeDecision(
        thesis="test",
        confidence=0.7,
        action=TradeAction.BUY,
        token="BNB",
        size_pct=2.0,
        reasoning="Go.",
    )
    risk = RiskAssessment(approved=True, regime=MarketRegime.TRENDING_BEAR, adjusted_size_pct=2.0)
    result = executor.execute(decision, risk)
    assert result["status"] == "executed"
    assert result["tx_hash"] == "0xabc"
    assert mock_run.call_count == 2
    assert "--quote-only" not in mock_run.call_args_list[1][0][0]


def test_twak_unconfigured_blocks_trade():
    executor = make_executor(twak_access_id="", twak_hmac_secret="")
    decision = TradeDecision(
        thesis="test",
        confidence=0.7,
        action=TradeAction.BUY,
        token="BNB",
        size_pct=2.0,
        reasoning="Go.",
    )
    risk = RiskAssessment(approved=True, regime=MarketRegime.TRENDING_BEAR, adjusted_size_pct=2.0)
    result = executor.execute(decision, risk)
    assert result["status"] == "twak_unconfigured"