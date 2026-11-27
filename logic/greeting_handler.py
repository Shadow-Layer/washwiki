import string

_GREETING_KEYWORDS = {
    "hi",
    "hey",
    "hello",
    "good morning",
    "good afternoon",
    "good evening",
    "mhoro",
    "makadii",
    "ndeipi",
    "sawubona",
    "howzit",
    "sup",
    "yo",
    "greetings",
}

_GREETING_RESPONSES = {
    "shona": {
        "short": (
            "Mhoro! Welcome to Wash Wiki. Ndibvunzei nezvemvura, kugeza maoko, "
            "zvimbuzi, kana kudzivirira zvirwere."
        ),
        "topics": ["Water Safety", "Handwashing", "Sanitation", "Disease Prevention"],
    },
    "en": {
        "short": (
            "Hello! Welcome to Wash Wiki. Ask me about water safety, handwashing, "
            "sanitation, or disease prevention."
        ),
        "topics": ["Water Safety", "Handwashing", "Sanitation", "Disease Prevention"],
    },
}


def _normalise_greeting(text: str) -> str:
    return " ".join(
        text.lower().translate(str.maketrans("", "", string.punctuation)).split()
    )


def is_greeting(user_input: str) -> bool:
    return _normalise_greeting(user_input) in _GREETING_KEYWORDS


def get_greeting_response(language: str = "shona") -> dict:
    return _GREETING_RESPONSES.get(language, _GREETING_RESPONSES["en"])
