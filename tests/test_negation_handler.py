import unittest

from logic.negation_handler import detect_negated_intent


class TestNegationHandler(unittest.TestCase):
    def test_no_soap_maps_to_handwash_no_soap(self):
        self.assertEqual(detect_negated_intent("no soap"), "handwash_no_soap")

    def test_handina_mvura_maps_to_no_clean_water(self):
        self.assertEqual(detect_negated_intent("handina mvura"), "no_clean_water")

    def test_no_toilet_maps_to_open_defecation(self):
        self.assertEqual(detect_negated_intent("no toilet"), "open_defecation")

    def test_no_problem_returns_none(self):
        self.assertIsNone(detect_negated_intent("no problem"))

    def test_do_not_drink_river_water_returns_none(self):
        self.assertIsNone(detect_negated_intent("do not drink river water"))


if __name__ == "__main__":
    unittest.main()
