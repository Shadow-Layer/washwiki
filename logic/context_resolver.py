from __future__ import annotations

import string

from logic.intent_matcher import match_intent

_WATER_SAFETY_TOPICS = {"water safety", "mvura yakachengeteka"}
_REFINEMENT_RULES = (
    (("child", "children", "baby", "mwana", "vana"), "child_sick", None),
    (("how long", "minutes", "maminitsi", "long"), "water_boil_how_long", _WATER_SAFETY_TOPICS),
    (("chlorine",), "water_chlorine", None),
    (("filter", "cloth", "sefa"), "water_sand_filter", _WATER_SAFETY_TOPICS),
    (("borehole", "well", "mugodhi", "pump"), "water_borehole", None),
    (("ors", "rehydration", "salts"), "ors_what", None),
    (("vegetable", "vegetables", "food wash", "miriwo"), "food_wash", None),
    (("store food", "keep food", "cover food", "food storage"), "food_store", None),
)


def _normalise(text: str) -> str:
    lowered = text.lower()
    cleaned = lowered.translate(str.maketrans("", "", string.punctuation))
    return " ".join(cleaned.split())


def _find_intent(intent_id: str, all_intents: list[dict]) -> dict | None:
    for intent in all_intents:
        if intent.get("intent_id") == intent_id:
            return intent
    return None


def resolve_contextual_input(
    user_input: str,
    last_intent_id: str | None,
    all_intents: list[dict],
) -> dict | None:
    if last_intent_id is None or len(user_input.strip().split()) > 5:
        return None

    normalised_input = _normalise(user_input)
    last_intent = _find_intent(last_intent_id, all_intents)
    if last_intent is None:
        return None

    last_topic = str(last_intent.get("topic", "")).lower()

    for triggers, intent_id, allowed_topics in _REFINEMENT_RULES:
        if allowed_topics is not None and last_topic not in allowed_topics:
            continue
        if any(trigger in normalised_input for trigger in triggers):
            return _find_intent(intent_id, all_intents)

    matched_intent = match_intent(user_input)
    if matched_intent is None:
        return None

    if str(matched_intent.get("topic", "")).lower() == last_topic:
        return matched_intent

    return None
