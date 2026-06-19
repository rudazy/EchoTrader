import json
from unittest.mock import MagicMock, patch

from agents.twak_client import TwakClient
from config.settings import Settings


def make_client(**overrides) -> TwakClient:
    base = {
        "twak_access_id": "access-123",
        "twak_hmac_secret": "secret-456",
        "twak_wallet_password": "TestPass1",
        "twak_chain": "bsc",
        "twak_quote_amount": "10",
    }
    base.update(overrides)
    return TwakClient(Settings(**base))


def test_credentials_configured():
    client = make_client()
    assert client.credentials_configured() is True
    assert make_client(twak_access_id="").credentials_configured() is False


@patch("agents.twak_client.subprocess.run")
def test_get_swap_quote_success(mock_run: MagicMock):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "input": "10.0 USDT",
            "output": "0.015 BNB",
            "provider": "1inch",
        }),
        stderr="",
    )
    client = make_client()
    result = client.get_swap_quote("USDT", "BNB", "10", "bsc")
    assert result["success"] is True
    assert result["quote"]["output"] == "0.015 BNB"
    assert "swap" in mock_run.call_args[0][0]
    assert "--quote-only" in mock_run.call_args[0][0]


@patch("agents.twak_client.subprocess.run")
def test_execute_swap_no_quote_only(mock_run: MagicMock):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({"hash": "0xabc", "explorer": "https://bscscan.com/tx/0xabc"}),
        stderr="",
    )
    client = make_client()
    result = client.execute_swap("USDT", "BNB")
    assert result["hash"] == "0xabc"
    assert "--quote-only" not in mock_run.call_args[0][0]


def test_health_check_reports_missing_creds():
    client = make_client(twak_access_id="", twak_hmac_secret="")
    health = client.health_check()
    assert health["credentials_configured"] is False
    assert health["auth"] is None