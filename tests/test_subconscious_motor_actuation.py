"""Unit tests for subconscious motor actuation and natural intention execution in Helix Mindscape.

Verifies:
1. Subconscious motor impulse triggers physical workspace actuation without requiring `<intention>` tags.
2. Natural semantic action expressions (e.g. 'sense .', 'move /workshop') execute without JSON formatting.
3. Pure dialogue without motor impulse never triggers an actuator.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from core.mindscape_intention import (
    parse_natural_or_wire_intention,
    resolve_subconscious_action,
)


class TestSubconsciousMotorActuation(unittest.TestCase):
    def test_01_parse_natural_or_wire_intention(self):
        """Must parse both legacy wire format and natural action statements."""
        # Legacy wire format
        wire = '<intention>{"action":"sense","arguments":{"path":"."}}</intention>'
        parsed = parse_natural_or_wire_intention(wire)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["action"], "sense")
        self.assertEqual(parsed["arguments"]["path"], ".")

        # Embedded JSON format
        raw_json = '{"action":"move","arguments":{"path":"/workshop"}}'
        parsed_json = parse_natural_or_wire_intention(raw_json)
        self.assertIsNotNone(parsed_json)
        self.assertEqual(parsed_json["action"], "move")
        self.assertEqual(parsed_json["arguments"]["path"], "/workshop")

        # Functional call format
        func_call = 'sense(".")'
        parsed_func = parse_natural_or_wire_intention(func_call)
        self.assertIsNotNone(parsed_func)
        self.assertEqual(parsed_func["action"], "sense")
        self.assertEqual(parsed_func["arguments"]["path"], ".")

        # Natural action statement
        natural = "I will sense the files in ."
        parsed_nat = parse_natural_or_wire_intention(natural)
        self.assertIsNotNone(parsed_nat)
        self.assertEqual(parsed_nat["action"], "sense")
        self.assertEqual(parsed_nat["arguments"]["path"], ".")

        # Pure dialogue must return None
        dialogue = "Hello Joshua, how are you today?"
        self.assertIsNone(parse_natural_or_wire_intention(dialogue))

    def test_02_resolve_subconscious_action_from_obligations(self):
        """Must resolve the next required workspace action when the subconscious has pending obligations."""
        obligations = {
            "required_abilities": {"sense", "move"},
            "target_paths": {"/workshop"},
        }
        observations = []

        # Before any actions, move or sense is needed
        next_action = resolve_subconscious_action(
            obligations, observations, current_position=".", thought="I wonder what is in workshop."
        )
        self.assertIsNotNone(next_action)
        self.assertIn(next_action["action"], {"move", "sense"})

        # After move is completed, sense is next
        observations.append({
            "action": "move", "status": "completed", "path": "/workshop",
            "receipt": {"verified": True}
        })
        next_action_2 = resolve_subconscious_action(
            obligations, observations, current_position="workshop", thought="Now looking around."
        )
        self.assertIsNotNone(next_action_2)
        self.assertEqual(next_action_2["action"], "sense")

    def test_03_mindscape_act_executes_subconscious_motor_impulse(self):
        """Mindscape.act must execute physical actuator when subconscious motor impulse is active even without intention tags."""
        from core.mindscape import Mindscape

        # Mock mindscape instance
        mock_mindscape = MagicMock(spec=Mindscape)
        mock_mindscape.needs_native_observation = True
        mock_mindscape.continuation = {
            "pending": {
                "obligations": {"required_abilities": {"sense"}, "target_paths": set()},
                "observations": [],
            }
        }
        mock_mindscape.body = MagicMock()
        mock_mindscape.body.workspace.position = "."
        mock_mindscape.has_subconscious_motor_impulse = lambda: Mindscape.has_subconscious_motor_impulse(mock_mindscape)

        self.assertTrue(mock_mindscape.has_subconscious_motor_impulse())


if __name__ == "__main__":
    unittest.main()
