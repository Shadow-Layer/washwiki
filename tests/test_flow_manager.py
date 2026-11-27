import unittest
from unittest.mock import patch

from logic.flow_manager import FlowManager


class TestFlowManager(unittest.TestCase):
    def setUp(self):
        language_manager_patcher = patch("logic.flow_manager.LanguageManager")
        self.addCleanup(language_manager_patcher.stop)
        self.mock_language_manager_cls = language_manager_patcher.start()
        self.mock_language_manager = self.mock_language_manager_cls.return_value
        self.mock_language_manager.detect_language_switch.return_value = None
        self.manager = FlowManager()

    @patch("logic.flow_manager.build_response")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_single_turn_river_water(self, mock_match_intent_with_candidates, mock_build_response):
        mock_match_intent_with_candidates.return_value = ({"intent_id": "water_river_safe"}, None)
        mock_build_response.return_value = {
            "short": "River water is unsafe without treatment.",
            "steps": ["Boil before drinking."],
            "warning": "Do not drink untreated river water.",
            "follow_up": "placeholder",
        }

        response = self.manager.process_message("session-1", "Can I drink river water?")

        self.assertEqual(response["intent_id"], "water_river_safe")
        self.assertEqual(
            response["follow_up"],
            "Is the water clear or dirty? / Mvura yakachena here kana yakasviba?",
        )
        self.assertEqual(
            self.manager._sessions["session-1"]["awaiting_follow_up"],
            "water_river_safe",
        )

    @patch("logic.flow_manager.build_response")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_followup_dirty_water_very_cloudy(
        self,
        mock_match_intent_with_candidates,
        mock_build_response,
    ):
        mock_match_intent_with_candidates.return_value = ({"intent_id": "dirty_water_action"}, None)
        mock_build_response.return_value = {
            "short": "Dirty water should be treated.",
            "steps": [],
            "warning": None,
            "follow_up": "placeholder",
        }

        self.manager.process_message("session-2", "My water is dirty")
        response = self.manager.process_message("session-2", "very cloudy")

        self.assertTrue(any("Filter the water first" in step for step in response["steps"]))

    @patch("logic.flow_manager.build_response")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_followup_dirty_water_slightly_dirty(
        self,
        mock_match_intent_with_candidates,
        mock_build_response,
    ):
        mock_match_intent_with_candidates.return_value = (
            {"intent_id": "dirty_water_action"},
            None,
        )
        mock_build_response.return_value = {
            "short": "Dirty water should be treated.",
            "steps": [],
            "warning": None,
            "follow_up": "placeholder",
        }

        self.manager.process_message("session-3", "My water is dirty")
        response = self.manager.process_message("session-3", "zvishoma")

        self.assertTrue(any("Boil the water" in step for step in response["steps"]))

    @patch("logic.flow_manager.build_response")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_followup_river_water_clear(
        self,
        mock_match_intent_with_candidates,
        mock_build_response,
    ):
        mock_match_intent_with_candidates.return_value = ({"intent_id": "water_river_safe"}, None)
        mock_build_response.return_value = {
            "short": "River water is unsafe without treatment.",
            "steps": [],
            "warning": None,
            "follow_up": "placeholder",
        }

        self.manager.process_message("session-4", "Can I drink river water?")
        response = self.manager.process_message("session-4", "clear")

        self.assertIn("invisible germs", response["short"])
        self.assertTrue(any("Boil the water" in step for step in response["steps"]))

    @patch("logic.flow_manager.build_response")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_followup_river_water_dirty(
        self,
        mock_match_intent_with_candidates,
        mock_build_response,
    ):
        mock_match_intent_with_candidates.return_value = ({"intent_id": "water_river_safe"}, None)
        mock_build_response.return_value = {
            "short": "River water is unsafe without treatment.",
            "steps": [],
            "warning": None,
            "follow_up": "placeholder",
        }

        self.manager.process_message("session-5", "Can I drink river water?")
        response = self.manager.process_message("session-5", "dirty")

        joined_steps = " ".join(response["steps"])
        self.assertIn("Filter", joined_steps)
        self.assertIn("Boil", joined_steps)

    @patch("logic.flow_manager.build_response")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_followup_no_soap_yes_ash(
        self,
        mock_match_intent_with_candidates,
        mock_build_response,
    ):
        mock_match_intent_with_candidates.return_value = ({"intent_id": "handwash_no_soap"}, None)
        mock_build_response.return_value = {
            "short": "You can use ash if soap is not available.",
            "steps": [],
            "warning": None,
            "follow_up": "placeholder",
        }

        self.manager.process_message("session-6", "I have no soap")
        response = self.manager.process_message("session-6", "hongu")

        self.assertTrue(any("ash" in step.lower() for step in response["steps"]))

    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_escalation(self, mock_match_intent_with_candidates):
        response = self.manager.process_message("session-7", "I am very sick")

        self.assertTrue(response["is_escalation"])
        mock_match_intent_with_candidates.assert_not_called()

    def test_language_switch(self):
        self.mock_language_manager.detect_language_switch.return_value = "en"

        response = self.manager.process_message("session-8", "speak English")

        self.assertEqual(self.manager._sessions["session-8"]["language"], "en")
        self.assertEqual(response["language"], "en")

    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_greeting_short_circuits_intent_matching(self, mock_match_intent_with_candidates):
        response = self.manager.process_message("session-greeting", "Hello!!!")

        self.assertIn("Wash Wiki", response["short"])
        self.assertEqual(
            response["topic_menu"],
            ["Water Safety", "Handwashing", "Sanitation", "Disease Prevention"],
        )
        mock_match_intent_with_candidates.assert_not_called()

    def test_topic_menu_water_safety(self):
        response = self.manager.process_message("session-9", "Water Safety")

        self.assertIsInstance(response["topic_menu"], list)
        self.assertTrue(response["topic_menu"])

    @patch("logic.flow_manager.get_ai_response", return_value=None)
    @patch("logic.flow_manager.get_fallback")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_fallback(
        self,
        mock_match_intent_with_candidates,
        mock_get_fallback,
        mock_get_ai_response,
    ):
        del mock_get_ai_response
        mock_match_intent_with_candidates.return_value = (None, None)
        mock_get_fallback.return_value = {
            "short": "I did not understand that.",
            "steps": [],
            "warning": None,
            "follow_up": None,
            "topics": ["Water Safety", "Handwashing"],
        }

        response = self.manager.process_message("session-10", "something unrelated")

        self.assertTrue(response["is_fallback"])
        self.assertEqual(response["topic_menu"], ["Water Safety", "Handwashing"])
        mock_get_fallback.assert_called_once_with("shona")

    @patch("logic.flow_manager.get_ai_response", return_value=None)
    @patch("logic.flow_manager.get_fallback")
    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_fallback_uses_existing_session_language(
        self,
        mock_match_intent_with_candidates,
        mock_get_fallback,
        mock_get_ai_response,
    ):
        del mock_get_ai_response
        mock_match_intent_with_candidates.return_value = (None, None)
        mock_get_fallback.return_value = {
            "short": "I didn't understand that.",
            "steps": [],
            "warning": None,
            "follow_up": None,
            "topics": ["Water Safety"],
        }
        self.manager._sessions["session-en"] = {
            "language": "en",
            "awaiting_follow_up": None,
            "follow_up_context": None,
            "last_intent_id": None,
        }

        response = self.manager.process_message("session-en", "something unrelated")

        self.assertEqual(response["language"], "en")
        mock_get_fallback.assert_called_once_with("en")

    @patch("logic.flow_manager.build_response")
    def test_negated_input_short_circuits_to_negated_intent(self, mock_build_response):
        mock_build_response.return_value = {
            "short": "Use ash if you do not have soap.",
            "steps": [],
            "warning": None,
            "follow_up": None,
        }

        response = self.manager.process_message("session-neg", "no soap")

        self.assertEqual(response["intent_id"], "handwash_no_soap")
        self.assertEqual(response["short"], "Use ash if you do not have soap.")

    @patch("logic.flow_manager.match_intent_with_candidates")
    def test_disambiguation_returns_candidate_topic_menu(self, mock_match_intent_with_candidates):
        mock_match_intent_with_candidates.return_value = (
            {
                "intent_id": "water_a",
                "canonical_question": {"en": "First water question", "shona": "Mvura yekutanga"},
            },
            {
                "intent_id": "water_b",
                "canonical_question": {"en": "Second water question", "shona": "Mvura yechipiri"},
            },
        )

        response = self.manager.process_message("session-disambiguation", "water question")

        self.assertTrue(response["is_disambiguation"])
        self.assertEqual(
            response["topic_menu"],
            ["Mvura yekutanga", "Mvura yechipiri"],
        )


if __name__ == "__main__":
    unittest.main()
