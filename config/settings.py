from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = PROJECT_ROOT / "memory"
LOGS_DIR = PROJECT_ROOT / "logs"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # CoinMarketCap
    cmc_api_key: str = ""
    cmc_mcp_url: str = "https://mcp.coinmarketcap.com/mcp"

    # x402
    x402_wallet_private_key: str = ""
    x402_enabled: bool = False

    # TWAK
    twak_access_id: str = ""
    twak_hmac_secret: str = ""
    twak_wallet_password: str = ""
    twak_chain: str = "bsc"
    twak_quote_amount: str = "10"

    # BNB Agent SDK
    bnb_agent_private_key: str = ""
    bnb_chain_id: int = 56

    # Guardrails
    dry_run: bool = True
    max_daily_drawdown_pct: float = 3.0
    max_position_size_pct: float = 5.0
    default_slippage_pct: float = 1.0
    cooldown_minutes: int = 60
    token_allowlist: str = "BNB,ETH,USDT,USDC"

    # Orchestrator
    loop_interval_seconds: int = 300
    log_level: str = "INFO"

    @field_validator("max_daily_drawdown_pct", "max_position_size_pct", "default_slippage_pct")
    @classmethod
    def positive_pct(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Percentage values must be positive")
        return value

    @property
    def allowed_tokens(self) -> list[str]:
        return [token.strip().upper() for token in self.token_allowlist.split(",") if token.strip()]

    @property
    def short_term_memory_path(self) -> Path:
        return MEMORY_DIR / "short_term.json"

    @property
    def lessons_path(self) -> Path:
        return MEMORY_DIR / "lessons.md"

    @property
    def trades_log_path(self) -> Path:
        return LOGS_DIR / "trades.log"

    def validate_runtime(self) -> None:
        missing: list[str] = []
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.cmc_api_key and not self.x402_enabled:
            missing.append("CMC_API_KEY (or enable X402_ENABLED)")
        if missing:
            raise RuntimeError(
                "Missing required environment variables: " + ", ".join(missing)
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()