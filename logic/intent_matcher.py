import json
import re
import string
from difflib import SequenceMatcher
from pathlib import Path

_CONTENT_DIR = Path(__file__).parent.parent / "content"
_CONTENT_FILES = (
    "water_safety.json",
    "handwashing.json",
    "sanitation.json",
    "disease_prevention.json",
)
_SUBSTITUTIONS = (
    ("stomach running", "diarrhoea"),
    ("running stomach", "diarrhoea"),
    ("loose stool", "diarrhoea"),
    ("loose stools", "diarrhoea"),
    ("water from the river", "river water"),
    ("water from river", "river water"),
    ("rwizi water", "river water"),
    ("mvura yerwizi", "river water"),
    ("mvura ye rwizi", "river water"),
    ("borehole water", "borehole"),
    ("well water", "well"),
    ("dam water", "dam"),
    ("tap water", "water"),
    ("purify water", "treat water"),
    ("purification", "treatment"),
    ("mvura yemugodhi", "borehole"),
    ("mvura yepombi", "borehole"),
    ("mvura yedhamu", "dam"),
    ("mvura yetap", "water"),
    ("masimu", "germs"),
    ("tsvina", "waste"),
    ("bika mvura", "boil water"),
    ("sefa mvura", "filter water"),
    ("korora", "cholera"),
    ("manyoka", "diarrhoea"),
    ("madota", "ash"),
    ("sipo", "soap"),
    ("maoko", "hands"),
    ("mvura", "water"),
    ("bika", "boil"),
    ("sefa", "filter"),
    ("kurapa", "treat"),
    ("chimbuzi", "toilet"),
    ("latrine", "toilet"),
)
STRONG_SIGNAL_TAGS = {
    "ors",
    "water",
    "toilet",
    "soap",
    "cholera",
    "diarrhoea",
    "handwashing",
    "mvura",
    "chimbuzi",
    "sipo",
    "korora",
    "manyoka",
}
FUZZY_THRESHOLD = 0.75
GENERIC_TAG_TOKENS = {
    "and",
    "at",
    "can",
    "clean",
    "do",
    "drink",
    "for",
    "from",
    "get",
    "help",
    "how",
    "is",
    "my",
    "of",
    "safe",
    "should",
    "the",
    "to",
    "what",
    "when",
    "why",
}
TOPIC_KEYWORD_INTENT_MAP = {
    "water": "water_safe",
    "mvura": "water_safe",
    "toilet": "toilet_why",
    "chimbuzi": "toilet_why",
    "soap": "handwash_no_soap",
    "sipo": "handwash_no_soap",
}


def _load_all_intents() -> list[dict]:
    intents: list[dict] = []
    for filename in _CONTENT_FILES:
        with (_CONTENT_DIR / filename).open("r", encoding="utf-8") as handle:
            intents.extend(json.load(handle))
    return intents


_ALL_INTENTS = _load_all_intents()


def get_all_intents() -> list[dict]:
    return _ALL_INTENTS


def reload_intents() -> None:
    global _ALL_INTENTS
    _ALL_INTENTS = _load_all_intents()


def _normalise(text: str) -> str:
    cleaned = text.lower()
    cleaned = cleaned.translate(str.maketrans("", "", string.punctuation))
    for raw, replacement in _SUBSTITUTIONS:
        cleaned = re.sub(rf"(?<!\w){re.escape(raw)}(?!\w)", replacement, cleaned)
    return " ".join(cleaned.split())


def _candidate_texts(intent: dict) -> list[str]:
    return [
        intent["canonical_question"]["en"],
        intent["canonical_question"]["shona"],
        *intent["sample_variations"]["en"],
        *intent["sample_variations"]["shona"],
    ]


def _best_candidate_ratio(intent: dict, normalised_input: str) -> float:
    return max(
        SequenceMatcher(None, normalised_input, _normalise(candidate)).ratio()
        for candidate in _candidate_texts(intent)
    )


def _match_exact_canonical_or_variation(normalised_input: str) -> dict | None:
    for intent in _ALL_INTENTS:
        canonical = intent["canonical_question"]
        if (
            normalised_input == _normalise(canonical["en"])
            or normalised_input == _normalise(canonical["shona"])
        ):
            return intent

    for intent in _ALL_INTENTS:
        for variation in intent["sample_variations"]["en"] + intent["sample_variations"]["shona"]:
            if normalised_input == _normalise(variation):
                return intent

    return None


def _match_tag_overlap(normalised_input: str) -> dict | None:
    exact_tag_matches = [
        intent
        for intent in _ALL_INTENTS
        if any(_normalise(tag) == normalised_input for tag in intent["tags"])
    ]
    if exact_tag_matches:
        preferred_intent_id = TOPIC_KEYWORD_INTENT_MAP.get(normalised_input)
        if preferred_intent_id is not None:
            for intent in exact_tag_matches:
                if intent["intent_id"] == preferred_intent_id:
                    return intent
        return max(
            exact_tag_matches,
            key=lambda intent: _best_candidate_ratio(intent, normalised_input),
        )

    best_phrase_intent: dict | None = None
    best_phrase_score = 0
    best_phrase_ratio = 0.0
    for intent in _ALL_INTENTS:
        matching_tags = [
            normalised_tag
            for tag in intent["tags"]
            if (normalised_tag := _normalise(tag)) and " " in normalised_tag
            if normalised_tag in normalised_input
        ]
        if not matching_tags:
            continue

        phrase_score = sum(len(tag.split()) for tag in matching_tags)
        ratio = _best_candidate_ratio(intent, normalised_input)
        if phrase_score > best_phrase_score or (
            phrase_score == best_phrase_score and ratio > best_phrase_ratio
        ):
            best_phrase_intent = intent
            best_phrase_score = phrase_score
            best_phrase_ratio = ratio

    return best_phrase_intent


def _match_keyword_score(normalised_input: str) -> dict | None:
    input_tokens = set(normalised_input.split())

    if len(input_tokens) == 1:
        preferred_intent_id = TOPIC_KEYWORD_INTENT_MAP.get(normalised_input)
        if preferred_intent_id is not None:
            for intent in _ALL_INTENTS:
                if intent["intent_id"] == preferred_intent_id:
                    return intent

    best_scoring_intent: dict | None = None
    best_score = 0
    best_strong_match = False
    best_ratio = 0.0

    for intent in _ALL_INTENTS:
        matched_tokens = {
            token
            for tag in intent["tags"]
            for token in _normalise(tag).split()
            if token in input_tokens and token not in GENERIC_TAG_TOKENS
        }
        score = len(matched_tokens)
        strong_match = any(token in STRONG_SIGNAL_TAGS for token in matched_tokens)
        ratio = _best_candidate_ratio(intent, normalised_input)
        if score > best_score or (
            score == best_score
            and (
                (strong_match and not best_strong_match)
                or (strong_match == best_strong_match and ratio > best_ratio)
            )
        ):
            best_scoring_intent = intent
            best_score = score
            best_strong_match = strong_match
            best_ratio = ratio

    if best_scoring_intent is not None and (
        best_score >= 2 or (best_score >= 1 and best_strong_match)
    ):
        return best_scoring_intent

    return None


def _match_fuzzy(normalised_input: str) -> dict | None:
    best_fuzzy_intent: dict | None = None
    best_ratio = 0.0

    for intent in _ALL_INTENTS:
        for candidate in _candidate_texts(intent):
            ratio = SequenceMatcher(None, normalised_input, _normalise(candidate)).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_fuzzy_intent = intent

    if best_fuzzy_intent is not None and best_ratio >= FUZZY_THRESHOLD:
        return best_fuzzy_intent

    return None


def _match_fuzzy_with_candidates(normalised_input: str) -> tuple[dict | None, dict | None]:
    ranked_intents = sorted(
        (
            (_best_candidate_ratio(intent, normalised_input), intent)
            for intent in _ALL_INTENTS
        ),
        key=lambda item: item[0],
        reverse=True,
    )

    if not ranked_intents or ranked_intents[0][0] < FUZZY_THRESHOLD:
        return None, None

    best_ratio, best_intent = ranked_intents[0]
    if len(ranked_intents) < 2:
        return best_intent, None

    second_ratio, second_intent = ranked_intents[1]
    if second_ratio >= FUZZY_THRESHOLD and best_ratio - second_ratio <= 0.05:
        return best_intent, second_intent

    return best_intent, None


def match_intent_with_candidates(
    user_input: str,
    language: str = "shona",
) -> tuple[dict | None, dict | None]:
    del language

    normalised_input = _normalise(user_input)
    exact_match = _match_exact_canonical_or_variation(normalised_input)
    if exact_match is not None:
        return exact_match, None

    tag_match = _match_tag_overlap(normalised_input)
    if tag_match is not None:
        return tag_match, None

    keyword_match = _match_keyword_score(normalised_input)
    if keyword_match is not None:
        return keyword_match, None

    return _match_fuzzy_with_candidates(normalised_input)


def match_intent(user_input: str, language: str = "shona") -> dict | None:
    intent, _ = match_intent_with_candidates(user_input, language)
    return intent
