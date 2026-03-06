import collections
import time
from typing import Optional


class MemoryBuffer:
    """
    Short-Term Memory (STM) for the AI Commentator.
    
    Acts as a sliding window of the last N significant events,
    preventing context saturation in Gemini while giving the LLM
    sufficient awareness to generate connected, non-repetitive commentary.
    
    Design Principle: Do not store everything. Store what matters.
    """

    def __init__(self, limit: int = 5, cooldown_seconds: float = 30.0):
        # Deque auto-evicts the oldest entry when full (zero-cost sliding window)
        self.history: collections.deque = collections.deque(maxlen=limit)
        self.cooldown_seconds = cooldown_seconds
        # Tracks the last time each event_type was used in commentary
        self.topic_cooldowns: dict = {}

    def add_event(self, event_type: str, summary: str) -> None:
        """
        Log a significant event into the Short-Term Memory.
        
        Args:
            event_type: Category of the event (e.g., 'CRASH', 'TIRE_TEMP', 'REBASE').
            summary:    Brief human-readable description of the event.
        """
        self.history.append({
            "time": time.time(),
            "type": event_type.upper(),
            "content": summary
        })
        # Stamp the last time this topic was active
        self.topic_cooldowns[event_type.upper()] = time.time()

    def get_context_string(self) -> str:
        """
        Serialize the event history into an injectable string for the LLM prompt.
        
        Returns a natural-language summary of recent events, ordered from oldest to newest,
        with relative time offsets so the LLM understands sequence and recency.
        
        Example output:
            "Recent Context: 35s ago → CRASH: Major incident at Turn 1 | 10s ago → TIRE_TEMP: Front-left overheating"
        """
        if not self.history:
            return "Contexto: Sin eventos previos relevantes. Es tu primer comentario de la sesión."

        now = time.time()
        fragments = []
        for event in self.history:  # deque preserves insertion order (oldest first)
            elapsed = int(now - event["time"])
            fragments.append(f"Hace {elapsed}s → {event['type']}: {event['content']}")

        return "Contexto Reciente: " + " | ".join(fragments)

    def is_redundant(self, event_type: str) -> bool:
        """
        Check if an event_type is still within its cooldown window.
        
        If True, the Orchestrator should suppress or deprioritize a new
        comment about this topic to avoid repetitive commentary.
        
        Args:
            event_type: The topic to check (e.g., 'TIRE_TEMP').
            
        Returns:
            True if the topic was mentioned within the cooldown window.
        """
        last_time = self.topic_cooldowns.get(event_type.upper(), 0.0)
        return (time.time() - last_time) < self.cooldown_seconds

    def clear(self) -> None:
        """Hard reset of the memory buffer (e.g., on /clear command or session restart)."""
        self.history.clear()
        self.topic_cooldowns.clear()

    def __len__(self) -> int:
        return len(self.history)

    def __repr__(self) -> str:
        return f"MemoryBuffer(events={len(self.history)}, cooldowns={list(self.topic_cooldowns.keys())})"
