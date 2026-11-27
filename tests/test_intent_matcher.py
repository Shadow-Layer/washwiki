import unittest
from unittest.mock import patch


class IntentMatcherTests(unittest.TestCase):
    def test_greeting_handler_matches_whole_input(self):
        from logic import is_greeting

        self.assertTrue(is_greeting("Hello!!!"))
        self.assertTrue(is_greeting(" good morning "))
        self.assertFalse(is_greeting("hello there"))

    def test_canonical_match_english(self):
        from logic import match_intent

        intent = match_intent("Can I drink river water?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_canonical_match_shona(self):
        from logic import match_intent

        intent = match_intent("Ndinganwa mvura yerwizi here?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_variation_match(self):
        from logic import match_intent

        intent = match_intent("Is river water safe to drink?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_normalise_rwizi_water(self):
        from logic import match_intent

        intent = match_intent("rwizi water")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_normalise_mvura_yerwizi(self):
        from logic import match_intent

        intent = match_intent("mvura yerwizi")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_running_stomach_maps_to_diarrhoea(self):
        from logic import match_intent

        intent = match_intent("running stomach")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "diarrhoea_what")

    def test_borehole_water_maps_to_borehole_intent(self):
        from logic import match_intent

        intent = match_intent("borehole water safe")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_borehole")

    def test_chlorine_keyword_matches_chlorine_intent(self):
        from logic import match_intent

        intent = match_intent("chlorine")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_chlorine")

    def test_manyoka_maps_to_diarrhoea(self):
        from logic import match_intent

        intent = match_intent("manyoka")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "diarrhoea_what")

    def test_new_intent_matches_ors(self):
        from logic import match_intent

        intent = match_intent("what is ORS")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "ors_what")

    def test_new_intent_matches_sand_filter(self):
        from logic import match_intent

        intent = match_intent("how to make sand filter")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_sand_filter")

    def test_new_intent_matches_borehole(self):
        from logic import match_intent

        intent = match_intent("borehole water safe")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_borehole")

    def test_new_intent_matches_chlorine_keyword(self):
        from logic import match_intent

        intent = match_intent("chlorine")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_chlorine")

    def test_new_intent_matches_child_sick(self):
        from logic import match_intent

        intent = match_intent("my child is sick")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "child_sick")

    def test_new_intent_matches_latrine_build(self):
        from logic import match_intent

        intent = match_intent("how to build latrine")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "latrine_build")

    def test_new_intent_matches_food_store(self):
        from logic import match_intent

        intent = match_intent("store food")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "food_store")

    def test_new_intent_matches_food_wash(self):
        from logic import match_intent

        intent = match_intent("wash vegetables")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "food_wash")

    def test_new_substitution_running_stomach(self):
        from logic import match_intent

        intent = match_intent("running stomach")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "diarrhoea_what")

    def test_tag_match_river(self):
        from logic import match_intent

        intent = match_intent("river")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_keyword_scoring_prefers_highest_score(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "first",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["clean container"],
            },
            {
                "intent_id": "second",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["clean container", "covered storage"],
            },
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("the container should stay clean and storage covered")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "second")

    def test_keyword_scoring_accepts_strong_signal_tag(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "strong",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["clean soap"],
            }
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("I need soap that is clean today")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "strong")

    def test_fuzzy_match_handles_typo(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "river",
                "canonical_question": {
                    "en": "Can I drink river water?",
                    "shona": "Ndinganwa mvura yerwizi here?",
                },
                "sample_variations": {
                    "en": ["Is river water safe to drink?"],
                    "shona": [],
                },
                "tags": ["safe drinking source"],
            }
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("Can I drink rivier water?")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "river")

    def test_keyword_scoring_matches_single_topic_keyword(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "water_topic",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["clean source water"],
            }
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("water")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_topic")

    def test_keyword_scoring_matches_toilet(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "sanitation_what",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["shared toilet space"],
            }
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("toilet")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "sanitation_what")

    def test_keyword_scoring_matches_sick(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "disease_protect",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["stay healthy when sick"],
            }
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("stay healthy")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "disease_protect")

    def test_fuzzy_match_handles_boil_typo_phrase(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "boil",
                "canonical_question": {
                    "en": "Why should I boil water?",
                    "shona": "Sei ndichifanira kubika mvura?",
                },
                "sample_variations": {
                    "en": ["How do I boil water?"],
                    "shona": [],
                },
                "tags": ["safe drinking source"],
            }
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("how do i boil watter")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "boil")

    def test_unknown_input_returns_none(self):
        from logic import match_intent

        self.assertIsNone(match_intent("xyzzy foobar"))

    def test_match_intent_with_candidates_returns_two_close_fuzzy_matches(self):
        from logic.intent_matcher import match_intent_with_candidates

        intents = [
            {
                "intent_id": "first",
                "canonical_question": {
                    "en": "How do I clean dirty water?",
                    "shona": "Ndinonatsa sei mvura yakasviba?",
                },
                "sample_variations": {"en": [], "shona": []},
                "tags": [],
            },
            {
                "intent_id": "second",
                "canonical_question": {
                    "en": "How can I clean dirty water?",
                    "shona": "Ndinganatsa sei mvura yakasviba?",
                },
                "sample_variations": {"en": [], "shona": []},
                "tags": [],
            },
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            first, second = match_intent_with_candidates("how clean dirty water")

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertEqual(first["intent_id"], "first")
        self.assertEqual(second["intent_id"], "second")

    def test_fallback_shona_message(self):
        from logic import get_fallback

        self.assertEqual(
            get_fallback("shona")["message"],
            "Handina kunyatsonzwisisa. Munogona kubvunza nezvemvura yakachengeteka, kugeza maoko, sanitation, kana kudzivirira zvirwere.",
        )

    def test_fallback_english_message(self):
        from logic import get_fallback

        self.assertEqual(
            get_fallback("en")["message"],
            "I didn't quite understand that. You can ask me about water safety, handwashing, sanitation, or disease prevention.",
        )

    def test_language_manager_default(self):
        from logic import LanguageManager

        self.assertEqual(LanguageManager().get_language("s1"), "shona")

    def test_language_manager_switch_english(self):
        from logic import LanguageManager

        manager = LanguageManager()
        self.assertEqual(manager.detect_language_switch("speak English"), "en")
        manager.set_language("s1", "en")
        self.assertEqual(manager.get_language("s1"), "en")

    def test_response_builder_language_fields(self):
        from logic import build_response, match_intent

        intent = match_intent("Can I drink river water?")
        self.assertIsNotNone(intent)
        self.assertEqual(
            build_response(intent, "en")["short"],
            intent["answer_short"]["en"],
        )
        self.assertEqual(
            build_response(intent, "shona")["short"],
            intent["answer_short"]["shona"],
        )


if __name__ == "__main__":
    unittest.main()
