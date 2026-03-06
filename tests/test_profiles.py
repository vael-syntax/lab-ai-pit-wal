"""
Tests for profiles/schema.py — Validating the polymorphic profile schema.

Verifies that both Broadcaster (Paco Boxes) and Copilot (El Comandante)
personas load correctly via Pydantic, and that strict_constraints
are properly enforced for both personality archetypes.
"""
import sys
from pathlib import Path
import yaml
import pytest

sys.path.append(str(Path(__file__).parent.parent))

from profiles.schema import ProfileSchema


class TestProfileSchemaValidation:
    """Validates that profile YAML files conform to the Pydantic schema."""

    def _load(self, filename: str) -> ProfileSchema:
        path = Path(__file__).parent.parent / "profiles" / filename
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return ProfileSchema(**data)

    def test_paco_boxes_loads_correctly(self):
        """The broadcaster profile must load without errors."""
        profile = self._load("paco_boxes.yaml")
        assert profile.name == "Paco Boxes"
        assert profile.vision.enabled is True

    def test_copilot_loads_correctly(self):
        """The copilot profile must load without errors."""
        profile = self._load("copilot.yaml")
        assert profile.name == "Comandante"
        assert profile.vision.enabled is True

    def test_paco_has_anti_hallucination_constraints(self):
        """Paco Boxes must have strict_constraints defined (anti-hallucination protocol)."""
        profile = self._load("paco_boxes.yaml")
        assert len(profile.strict_constraints) > 0, "Paco needs anti-hallucination constraints."
        
        # Verify the tire constraint specifically is present
        tire_constraint = any("tire" in c.lower() or "neumático" in c.lower() 
                              for c in profile.strict_constraints)
        assert tire_constraint, "Missing tire/telemetry hallucination constraint in paco_boxes.yaml"

    def test_copilot_has_constraints_with_brevity_rule(self):
        """El Comandante must have the brevity rule as a constraint."""
        profile = self._load("copilot.yaml")
        assert len(profile.strict_constraints) > 0
        brevity = any("word" in c.lower() or "sentence" in c.lower() or "maximum" in c.lower()
                      for c in profile.strict_constraints)
        assert brevity, "Copiloto needs a brevity rule to enforce sub-8-word responses."

    def test_profiles_are_architecturally_distinct(self):
        """The two profiles must represent genuinely different operational modes."""
        paco = self._load("paco_boxes.yaml")
        copilot = self._load("copilot.yaml")
        
        # Different names and namespaces
        assert paco.name != copilot.name
        assert paco.memory_namespace != copilot.memory_namespace
        
        # Copilot should have higher stability (military, no emotion)
        assert copilot.voice.stability > paco.voice.stability, \
            "Copilot voice should be more stable/neutral than broadcaster."
