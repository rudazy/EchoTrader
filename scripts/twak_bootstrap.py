"""Bootstrap TWAK wallet and verify auth — run locally or on Railway."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.twak_client import TwakClient
from config.settings import get_settings


def main() -> None:
    settings = get_settings()
    client = TwakClient(settings)
    issues = settings.validate_twak()
    report = {
        "config_issues": issues,
        "health": client.health_check(),
        "wallet_bootstrap": client.ensure_wallet(),
    }
    print(json.dumps(report, indent=2, default=str))
    if issues and settings.twak_enabled:
        sys.exit(1)


if __name__ == "__main__":
    main()