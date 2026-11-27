_SHONA_MSG = (
    "Handina kunyatsonzwisisa. Munogona kubvunza nezvemvura yakachengeteka, "
    "kugeza maoko, sanitation, kana kudzivirira zvirwere."
)
_EN_MSG = (
    "I didn't quite understand that. You can ask me about water safety, "
    "handwashing, sanitation, or disease prevention."
)
_TOPICS = ["Water Safety", "Handwashing", "Sanitation", "Disease Prevention"]


def get_fallback(language: str = "en") -> dict:
    message = _EN_MSG if language == "en" else _SHONA_MSG
    return {
        "message": message,
        "short": message,
        "steps": _TOPICS,
        "topics": _TOPICS,
    }
