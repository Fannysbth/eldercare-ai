"""
session_manager.py
──────────────────
Lightweight in-memory session store for MVP.
Tracks longitudinal cognitive signals across a single browser session.
"""

from datetime import datetime


class SessionManager:
    def __init__(self):
        self.entries = []
        self.started_at = datetime.now().isoformat()

    def add_entry(self, text: str, scores: dict):
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "scores": scores,
        })

    def get_trend(self) -> dict:
        """Return simple trend analysis over session entries."""
        if len(self.entries) < 2:
            return {"trend": "insufficient_data"}

        scores = [e["scores"].get("composite_score", 0) for e in self.entries]
        first_half = sum(scores[: len(scores) // 2]) / max(len(scores) // 2, 1)
        second_half = sum(scores[len(scores) // 2 :]) / max(len(scores) - len(scores) // 2, 1)
        delta = second_half - first_half

        if delta > 10:
            trend = "worsening"
        elif delta < -10:
            trend = "improving"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "delta": round(delta, 1),
            "entry_count": len(self.entries),
        }
