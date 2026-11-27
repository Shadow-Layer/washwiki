from __future__ import annotations

import re
import string

_NEGATION_MARKERS = (
    "don't have",
    "do not have",
    "i have no",
    "not have",
    "without",
    "can't find",
    "cannot find",
    "hapana",
    "handina",
    "pasina",
    "isipo",
    "haisipo",
)

_SIGNAL_PATTERNS = (
    (re.compile(r"\b(clean water|safe water|water|mvura)\b"), "no_clean_water"),
    (re.compile(r"\b(soap|sipo)\b"), "handwash_no_soap"),
    (re.compile(r"\b(toilet|chimbuzi|latrine)\b"), "open_defecation"),
    (re.compile(r"\b(filter|cloth|sefa)\b"), "dirty_water_action"),
    (re.compile(r"\b(ash|madota)\b"), "no_soap_action"),
)
_DIRECT_NO_RESOURCE_PATTERNS = (
    (re.compile(r"\bno\s+(clean water|safe water|water|mvura)\b"), "no_clean_water"),
    (re.compile(r"\bno\s+(soap|sipo)\b"), "handwash_no_soap"),
    (re.compile(r"\bno\s+(toilet|chimbuzi|latrine)\b"), "open_defecation"),
    (re.compile(r"\bno\s+(filter|cloth|sefa)\b"), "dirty_water_action"),
    (re.compile(r"\bno\s+(ash|madota)\b"), "no_soap_action"),
)


def _normalise(text: str) -> str:
    lowered = text.lower()
    cleaned = lowered.translate(str.maketrans("", "", string.punctuation))
    return " ".join(cleaned.split())


def detect_negated_intent(user_input: str) -> str | None:
    normalised_input = _normalise(user_input)

    for pattern, intent_id in _DIRECT_NO_RESOURCE_PATTERNS:
        if pattern.search(normalised_input):
            return intent_id

    if not any(marker in normalised_input for marker in _NEGATION_MARKERS):
        return None

    for pattern, intent_id in _SIGNAL_PATTERNS:
        if pattern.search(normalised_input):
            return intent_id

    return None
