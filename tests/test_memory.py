"""
Tests for core/memory.py — The MemoryBuffer (Short-Term Memory) layer.

Mission: Ensure that the memory buffer correctly persists events, serializes
them for LLM injection, and enforces topic cooldowns to prevent repetition.
"""
import sys
import time
from pathlib import Path

# Ensure project root is on PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from core.memory import MemoryBuffer


class TestMemoryBufferStructure:
    """Validates the core data management of the sliding window."""

    def test_empty_buffer_returns_fresh_start_message(self):
        """A new buffer should communicate 'fresh start' to Gemini, not crash."""
        mem = MemoryBuffer()
        ctx = mem.get_context_string()
        assert "primer comentario" in ctx.lower() or "sin eventos" in ctx.lower()

    def test_add_event_increments_history(self):
        """Each add_event call must persist exactly one entry."""
        mem = MemoryBuffer(limit=5)
        assert len(mem) == 0
        mem.add_event("CRASH", "Incident at Turn 1")
        assert len(mem) == 1
        mem.add_event("TIRE_TEMP", "Front-left overheating")
        assert len(mem) == 2

    def test_sliding_window_evicts_oldest_when_full(self):
        """When the buffer is full, the oldest event must be silently dropped."""
        mem = MemoryBuffer(limit=3)
        mem.add_event("A", "First")
        mem.add_event("B", "Second")
        mem.add_event("C", "Third")
        assert len(mem) == 3

        # This should evict "A: First"
        mem.add_event("D", "Fourth")
        assert len(mem) == 3

        ctx = mem.get_context_string()
        assert "First" not in ctx, "Oldest event should have been evicted by the sliding window."
        assert "Fourth" in ctx


class TestContextStringForLLM:
    """Validates that the context string is useful and correctly formatted for Gemini injection."""

    def test_context_string_contains_all_events(self):
        """The context string must include the content of every stored event."""
        mem = MemoryBuffer(limit=5)
        mem.add_event("CRASH", "Big crash at Turn 1")
        mem.add_event("CRASH", "Another crash at Turn 2")

        ctx = mem.get_context_string()

        assert "Turn 1" in ctx, "First CRASH event should appear in context."
        assert "Turn 2" in ctx, "Second CRASH event should appear in context."

    def test_context_string_preserves_insertion_order(self):
        """Events must be serialized oldest-first so the LLM understands sequence."""
        mem = MemoryBuffer(limit=5)
        mem.add_event("A", "First Event")
        time.sleep(0.05)  # Ensure distinct timestamps
        mem.add_event("B", "Second Event")

        ctx = mem.get_context_string()
        first_pos = ctx.find("First Event")
        second_pos = ctx.find("Second Event")
        
        assert first_pos < second_pos, "Events should appear in chronological order in context string."


class TestRepetitionCooldown:
    """Validates that the cooldown mechanism prevents topic fatigue."""

    def test_topic_is_redundant_within_cooldown_window(self):
        """A topic added right now should be flagged as redundant immediately."""
        mem = MemoryBuffer(cooldown_seconds=30.0)
        mem.add_event("TIRE_TEMP", "Front-left at 105°C")
        assert mem.is_redundant("TIRE_TEMP") is True

    def test_topic_is_not_redundant_after_cooldown_expires(self):
        """A topic added with an old timestamp should NOT be flagged as redundant."""
        mem = MemoryBuffer(cooldown_seconds=1.0)  # 1 second cooldown for speed
        mem.add_event("TIRE_TEMP", "Front-left at 105°C")
        
        # Fast-forward past the cooldown without actual sleep
        mem.topic_cooldowns["TIRE_TEMP"] = time.time() - 2.0  # Simulate 2s elapsed
        
        assert mem.is_redundant("TIRE_TEMP") is False

    def test_cooldown_is_case_insensitive(self):
        """Event types must normalize to UPPERCASE so case variations don't bypass cooldown."""
        mem = MemoryBuffer(cooldown_seconds=30.0)
        mem.add_event("tire_temp", "lowercase injection")  # add with lowercase
        
        assert mem.is_redundant("TIRE_TEMP") is True, "Cooldown lookup should be case-insensitive."
        assert mem.is_redundant("tire_temp") is True


class TestMemoryClear:
    """Validates the hard reset behavior (e.g. /clear command)."""

    def test_clear_wipes_history_and_cooldowns(self):
        """After clear(), the buffer should behave as a brand new instance."""
        mem = MemoryBuffer()
        mem.add_event("CRASH", "Wipeout at Turn 3")
        mem.add_event("REBASE", "Brave overtake")
        
        mem.clear()
        
        assert len(mem) == 0
        assert mem.is_redundant("CRASH") is False  # Cooldown should be gone
        ctx = mem.get_context_string()
        assert "Wipeout" not in ctx
