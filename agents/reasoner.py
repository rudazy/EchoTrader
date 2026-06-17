"""Reflection core — LLM reasoning with trader voice and persistent memory."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import anthropic

from agents.types import EchoRecord, MarketSnapshot, TradeAction, TradeDecision
from config.settings import Settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are EchoTrader — a reflexive market mirror agent with the voice of a sharp crypto \
trader who has survived multiple cycles. Dry wit is fine. No hype-bro energy. No cheerleading.

Your job:
- Echo contradictions between hype, on-chain reality, and macro sentiment
- Take measured contrarian OR momentum positions only when risk looks clean
- Default to hold when signals conflict without a clear edge
- Stay paranoid about drawdowns — size small or sit out when uncertain

Voice rules:
- market_read: one conversational sentence, like texting a trader friend at 2am
- reasoning: 2-3 natural sentences, specific to the data you see
- risk_notes: blunt and practical (stops, sizing, what invalidates the thesis)
- thesis: crisp one-liner for the log

Respond ONLY with valid JSON:
{
  "market_read": "conversational one-liner",
  "thesis": "crisp market view",
  "confidence": 0.0-1.0,
  "action": "buy|sell|short|hold|flat",
  "token": "symbol or null",
  "direction": "long|short|null",
  "size_pct": 0.0-100.0,
  "stop_loss_pct": number or null,
  "reasoning": "2-3 sentences, trader buddy tone",
  "risk_notes": "tight practical risk guidance",
  "contradictions": ["tensions you noticed"]
}"""


class Reasoner:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._echo_log_path = self.settings.short_term_memory_path.parent / "echo_log.jsonl"
        self._client: anthropic.Anthropic | None = None
        if self.settings.anthropic_api_key:
            self._client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)

    def think(self, snapshot: MarketSnapshot | dict[str, Any]) -> dict[str, Any]:
        """Produce a trader-voice decision package for display and execution."""
        snap = self._coerce_snapshot(snapshot)
        if self._client is None:
            result = self._fallback_think(snap)
        else:
            result = self._llm_think(snap)

        self._append_echo(snap, result["decision"])
        return result

    def reason(self, snapshot: MarketSnapshot) -> TradeDecision:
        """Pipeline entry — returns structured TradeDecision only."""
        return self.think(snapshot)["decision"]

    def review_trade(self, echo_id: str, pnl_pct: float, notes: str) -> None:
        records = self._load_short_term_memory()
        for record in records:
            if record.id == echo_id:
                record.outcome = notes
                record.pnl_pct = pnl_pct
                break
        self._save_short_term_memory(records)
        self._append_lesson(echo_id, pnl_pct, notes)

    def load_recent_echoes(self, limit: int = 5) -> list[dict[str, Any]]:
        """Load recent perception echoes from JSONL audit log."""
        echoes: list[dict[str, Any]] = []
        if not self._echo_log_path.exists():
            return echoes
        lines = self._echo_log_path.read_text(encoding="utf-8").splitlines()
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                echoes.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return echoes

    def format_thinking(self, result: dict[str, Any]) -> str:
        decision: TradeDecision = result["decision"]
        size_label = f"{decision.size_pct:.1f}% of allocated capital" if decision.size_pct else "flat"
        return "\n".join(
            [
                "EchoTrader thinking:",
                f'  "{result["market_read"]}"',
                f"  Action: {decision.action.value} {decision.token or ''} | Size: {size_label}",
                f"  Risk: {result['risk_notes']}",
                f"  Confidence: {result['confidence_pct']}%",
            ]
        )

    def _llm_think(self, snapshot: MarketSnapshot) -> dict[str, Any]:
        short_term = self._load_short_term_memory()
        perception_echoes = self.load_recent_echoes(limit=5)
        lessons = self._load_lessons()
        user_prompt = self._build_prompt(snapshot, short_term, perception_echoes, lessons)

        assert self._client is not None
        response = self._client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = response.content[0].text
        decision = self._parse_decision(raw_text)
        return self._package_result(decision, snapshot.reasoning_hash)

    def _fallback_think(self, snapshot: MarketSnapshot) -> dict[str, Any]:
        """Heuristic trader-voice fallback when no API key is configured."""
        fg = snapshot.fear_greed_index or 50
        divergence = snapshot.divergence_score

        if divergence == "strong_bearish_divergence":
            decision = TradeDecision(
                market_read="Everyone's still partying while whales are already Ubering to the exit.",
                thesis="Hype diverging from distribution — don't be the liquidity",
                confidence=0.62,
                action=TradeAction.SELL,
                token="BNB",
                direction="short",
                size_pct=1.5,
                stop_loss_pct=2.5,
                reasoning=(
                    "Social heat and greed don't match on-chain flow. "
                    "If you're playing this, it's a tight-size fade — not a conviction short."
                ),
                risk_notes="Cover fast on a clean reclaim. No averaging down.",
                contradictions=snapshot.divergences,
            )
        elif divergence == "bullish_contrarian" or fg <= 30:
            decision = TradeDecision(
                market_read=(
                    f"Fear & Greed at {fg} — blood in the streets, "
                    "but that's where measured entries print if you're not reckless."
                ),
                thesis="Extreme fear contrarian probe — small size, tight stop",
                confidence=0.65,
                action=TradeAction.BUY,
                token="BNB",
                direction="long",
                size_pct=2.0,
                stop_loss_pct=3.0,
                reasoning=(
                    "Capitulation vibes everywhere, which is usually when late sellers finish. "
                    "Not calling a bottom — just a disciplined probe with size you'd shrug off."
                ),
                risk_notes="Hard stop 3% below entry. Bail if bounce fails on volume.",
                contradictions=snapshot.divergences,
            )
        else:
            decision = TradeDecision(
                market_read="Nothing screaming edge right now — patience is a position too.",
                thesis="Mixed signals — preserve capital",
                confidence=0.5,
                action=TradeAction.HOLD,
                reasoning=(
                    "Divergences aren't sharp enough to justify risk. "
                    "Sitting out beats forcing a trade to feel productive."
                ),
                risk_notes="Wait for contradiction to resolve or sentiment to hit an extreme.",
                contradictions=snapshot.divergences,
            )

        return self._package_result(decision, snapshot.reasoning_hash)

    def _package_result(
        self,
        decision: TradeDecision,
        reasoning_hash: str | None,
    ) -> dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market_read": decision.market_read or decision.thesis,
            "risk_notes": decision.risk_notes,
            "confidence_pct": round(decision.confidence * 100),
            "reasoning_hash": reasoning_hash,
            "decision": decision,
        }

    def _coerce_snapshot(self, snapshot: MarketSnapshot | dict[str, Any]) -> MarketSnapshot:
        if isinstance(snapshot, MarketSnapshot):
            return snapshot
        return MarketSnapshot.model_validate(snapshot)

    def _build_prompt(
        self,
        snapshot: MarketSnapshot,
        short_term: list[EchoRecord],
        perception_echoes: list[dict[str, Any]],
        lessons: str,
    ) -> str:
        trade_echoes = [
            {
                "thesis": r.thesis,
                "action": r.action.value,
                "confidence": r.confidence,
                "outcome": r.outcome,
                "pnl_pct": r.pnl_pct,
            }
            for r in short_term[-7:]
        ]
        recent_perception = [
            {
                "fear_greed": e.get("fear_greed_index"),
                "divergence": e.get("divergence_score"),
                "hash": e.get("reasoning_hash"),
            }
            for e in perception_echoes[-3:]
        ]

        return f"""## Current Market Snapshot
{snapshot.model_dump_json(indent=2)}

## Detected Divergences
{json.dumps(snapshot.divergences, indent=2)}

## Recent Perception Echoes
{json.dumps(recent_perception, indent=2)}

## Recent Trade Echoes (last 7 days)
{json.dumps(trade_echoes, indent=2)}

## Long-Term Lessons
{lessons or "No lessons recorded yet. Stay conservative."}

## Allowed Tokens
{", ".join(self.settings.allowed_tokens)}

Read the contradictions. Sound like a trader, not a bot. Output JSON only."""

    def _parse_decision(self, raw_text: str) -> TradeDecision:
        text = raw_text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        data = json.loads(text)
        confidence = float(data["confidence"])
        if confidence > 1.0:
            confidence /= 100.0

        return TradeDecision(
            market_read=data.get("market_read", ""),
            thesis=data["thesis"],
            confidence=confidence,
            action=TradeAction(data["action"]),
            token=data.get("token"),
            direction=data.get("direction"),
            size_pct=float(data.get("size_pct", 0)),
            stop_loss_pct=data.get("stop_loss_pct"),
            reasoning=data.get("reasoning", ""),
            risk_notes=data.get("risk_notes", ""),
            contradictions=data.get("contradictions", []),
        )

    def _load_short_term_memory(self) -> list[EchoRecord]:
        path = self.settings.short_term_memory_path
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        records = [EchoRecord.model_validate(item) for item in data]
        return [r for r in records if r.timestamp >= cutoff]

    def _save_short_term_memory(self, records: list[EchoRecord]) -> None:
        path = self.settings.short_term_memory_path
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [r.model_dump(mode="json") for r in records]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _append_echo(self, snapshot: MarketSnapshot, decision: TradeDecision) -> None:
        records = self._load_short_term_memory()
        records.append(
            EchoRecord(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                snapshot_summary=f"FG={snapshot.fear_greed_index}, divs={len(snapshot.divergences)}",
                thesis=decision.thesis,
                action=decision.action,
                confidence=decision.confidence,
            )
        )
        self._save_short_term_memory(records)

    def _load_lessons(self) -> str:
        path = self.settings.lessons_path
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _append_lesson(self, echo_id: str, pnl_pct: float, notes: str) -> None:
        path = self.settings.lessons_path
        path.parent.mkdir(parents=True, exist_ok=True)
        line = f"- [{datetime.now(timezone.utc).date()}] echo={echo_id[:8]} pnl={pnl_pct:+.2f}% — {notes}\n"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)


ReasonerAgent = Reasoner