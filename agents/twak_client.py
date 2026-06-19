"""Trust Wallet Agent Kit (TWAK) CLI wrapper — install, auth, wallet, swap."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from typing import Any

from config.settings import Settings

logger = logging.getLogger(__name__)

TWAK_TIMEOUT_SECONDS = 45
TWAK_NPM_PACKAGE = "@trustwallet/cli@0.19.1"


class TwakClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def command_prefix(self) -> list[str]:
        if self.settings.twak_cli:
            return self.settings.twak_cli.split()
        if shutil.which("twak"):
            return ["twak"]
        if shutil.which("npx"):
            return ["npx", "--yes", TWAK_NPM_PACKAGE]
        return ["twak"]

    def build_env(self) -> dict[str, str]:
        env = os.environ.copy()
        if self.settings.twak_access_id:
            env["TWAK_ACCESS_ID"] = self.settings.twak_access_id
        if self.settings.twak_hmac_secret:
            env["TWAK_HMAC_SECRET"] = self.settings.twak_hmac_secret
        if self.settings.twak_wallet_password:
            env["TWAK_WALLET_PASSWORD"] = self.settings.twak_wallet_password
        return env

    def run(self, args: list[str], timeout: int = TWAK_TIMEOUT_SECONDS) -> dict[str, Any]:
        cmd = self.command_prefix() + args
        env = self.build_env()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                env=env,
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            for stream in (stdout, stderr):
                if not stream:
                    continue
                try:
                    parsed = json.loads(stream)
                    if isinstance(parsed, dict):
                        parsed.setdefault("returncode", proc.returncode)
                        return parsed
                    if isinstance(parsed, list):
                        return {
                            "data": parsed,
                            "raw": True,
                            "returncode": proc.returncode,
                        }
                except json.JSONDecodeError:
                    if stream is stdout:
                        return {"output": stdout, "raw": True, "returncode": proc.returncode}
            detail = stderr or stdout or "empty stdout"
            return {
                "error": detail,
                "errorCode": "UNKNOWN_ERROR",
                "returncode": proc.returncode,
            }
        except FileNotFoundError:
            return {
                "error": (
                    "twak CLI not found — install: npm install -g @trustwallet/cli "
                    "or set TWAK_CLI=npx"
                ),
                "errorCode": "CLI_NOT_FOUND",
            }
        except subprocess.TimeoutExpired:
            return {"error": "TWAK command timed out", "errorCode": "TIMEOUT"}

    def cli_available(self) -> bool:
        prefix = self.command_prefix()
        if prefix[0] == "twak":
            return shutil.which("twak") is not None or shutil.which("npx") is not None
        if prefix[0] == "npx":
            return shutil.which("npx") is not None
        return True

    def credentials_configured(self) -> bool:
        return bool(self.settings.twak_access_id and self.settings.twak_hmac_secret)

    def wallet_password_configured(self) -> bool:
        return bool(self.settings.twak_wallet_password)

    def auth_status(self) -> dict[str, Any]:
        if not self.credentials_configured():
            return {
                "ok": False,
                "error": "TWAK_ACCESS_ID and TWAK_HMAC_SECRET required",
                "errorCode": "CREDS_MISSING",
            }
        result = self.run(["auth", "status", "--json"])
        if result.get("error") or result.get("errorCode"):
            return {"ok": False, **result}
        return {"ok": True, "details": result}

    def wallet_status(self) -> dict[str, Any]:
        if not self.wallet_password_configured():
            return {
                "ok": False,
                "ready": False,
                "error": "TWAK_WALLET_PASSWORD not set — quotes work, swaps need password",
                "errorCode": "WALLET_PASSWORD_MISSING",
            }
        result = self.run(["wallet", "portfolio", "--json"])
        if result.get("error") or result.get("errorCode"):
            code = str(result.get("errorCode", ""))
            if code in {"WALLET_NOT_FOUND", "CLI_NOT_FOUND"}:
                return {"ok": False, "ready": False, **result}
            if "wallet" in str(result.get("error", "")).lower() and "not found" in str(result.get("error", "")).lower():
                return {"ok": False, "ready": False, **result}
        if result.get("data") or result.get("raw") or result.get("chain"):
            return {"ok": True, "ready": True, "portfolio": result}
        if result.get("error"):
            return {"ok": False, "ready": False, **result}
        return {"ok": True, "ready": True, "portfolio": result}

    def ensure_wallet(self) -> dict[str, Any]:
        """Create agent wallet in CI/container when password is set and wallet missing."""
        if not self.credentials_configured():
            return {"ok": False, "error": "TWAK credentials missing", "errorCode": "CREDS_MISSING"}
        if not self.wallet_password_configured():
            return {
                "ok": False,
                "skipped": True,
                "reason": "TWAK_WALLET_PASSWORD not set",
            }

        status = self.wallet_status()
        if status.get("ready"):
            return {"ok": True, "action": "existing_wallet"}

        create = self.run(
            [
                "wallet",
                "create",
                "--password",
                self.settings.twak_wallet_password,
                "--skip-password-check",
                "--json",
            ]
        )
        if create.get("error") and "already" not in str(create.get("error", "")).lower():
            return {"ok": False, "action": "create_failed", **create}
        return {"ok": True, "action": "created", "details": create}

    def get_swap_quote(
        self,
        from_token: str,
        to_token: str,
        amount: str | None = None,
        chain: str | None = None,
        slippage_pct: float | None = None,
    ) -> dict[str, Any]:
        amount = amount or self.settings.twak_quote_amount
        chain = chain or self.settings.twak_chain
        slippage = slippage_pct if slippage_pct is not None else self.settings.default_slippage_pct
        quote = self.run(
            [
                "swap",
                amount,
                from_token,
                to_token,
                "--chain",
                chain,
                "--slippage",
                str(slippage),
                "--quote-only",
                "--json",
            ]
        )
        success = "error" not in quote and "errorCode" not in quote
        return {
            "success": success,
            "quote": quote if success else None,
            "error": quote.get("error") if not success else None,
            "error_code": quote.get("errorCode", "UNKNOWN_ERROR") if not success else None,
        }

    def execute_swap(
        self,
        from_token: str,
        to_token: str,
        amount: str | None = None,
        chain: str | None = None,
        slippage_pct: float | None = None,
    ) -> dict[str, Any]:
        amount = amount or self.settings.twak_quote_amount
        chain = chain or self.settings.twak_chain
        slippage = slippage_pct if slippage_pct is not None else self.settings.default_slippage_pct
        return self.run(
            [
                "swap",
                amount,
                from_token,
                to_token,
                "--chain",
                chain,
                "--slippage",
                str(slippage),
                "--json",
            ]
        )

    def health_check(self) -> dict[str, Any]:
        return {
            "enabled": self.settings.twak_enabled,
            "cli": self.command_prefix(),
            "cli_available": self.cli_available(),
            "credentials_configured": self.credentials_configured(),
            "wallet_password_configured": self.wallet_password_configured(),
            "chain": self.settings.twak_chain,
            "bnb_chain_id": self.settings.bnb_chain_id,
            "dry_run": self.settings.dry_run,
            "auth": self.auth_status() if self.credentials_configured() else None,
            "wallet": self.wallet_status() if self.credentials_configured() else None,
        }