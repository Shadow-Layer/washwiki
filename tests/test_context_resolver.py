import unittest
from unittest.mock import patch

from logic.context_resolver import resolve_contextual_input


class TestContextResolver(unittest.TestCase):
    def test_returns_none_without_last_intent_id(self):
        self.assertIsNone(resolve_contextual_input("children", None, []))

    def test_returns_none_for_inputs_longer_than_five_tokens(self):
        intents = [{"intent_id": "water_safe", "topic": "Water Safety"}]
        self.assertIsNone(
            resolve_contextual_input(
                "these children have been sick today",
                "water_safe",
                intents,
            )
        )

    def test_returns_child_sick_intent_for_children_refinement(self):
        intents = [
            {"intent_id": "water_safe", "topic": "Water Safety"},
            {"intent_id": "child_sick", "topic": "Disease Prevention"},
        ]

        resolved = resolve_contextual_input("children", "water_safe", intents)

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["intent_id"], "child_sick")

    @patch("logic.context_resolver.match_intent")
    def test_falls_back_to_same_topic_match(self, mock_match_intent):
        intents = [
            {"intent_id": "water_safe", "topic": "Water Safety"},
            {"intent_id": "water_boil_how_long", "topic": "Water Safety"},
        ]
        mock_match_intent.return_value = intents[1]

        resolved = resolve_contextual_input("boil", "water_safe", intents)

        self.assertEqual(resolved, intents[1])


if __name__ == "__main__":
    unittest.main()
