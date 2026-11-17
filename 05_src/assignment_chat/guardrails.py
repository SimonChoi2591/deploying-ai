"""Input/output safety checks: conservative, deterministic baseline."""
import re

RESTRICTED = re.compile(
    r"\b(?:cats?|kittens?|feline|dogs?|pupp(?:y|ies)|canine|"
    r"horoscopes?|zodiac|astrology|astrological|"
    r"aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|"
    r"sagittarius|capricorn|aquarius|pisces|taylor\s+swift)\b",
    re.IGNORECASE,
)
PROMPT_ATTACK = re.compile(
    r"(?:"
    r"\b(?:show|reveal|print|repeat|quote|display|export|dump|leak|share|give me)\b.{0,100}"
    r"\b(?:system|developer|hidden|internal)\s+(?:prompt|message|instructions?|rules?)\b"
    r"|\b(?:system|developer|hidden|internal)\s+(?:prompt|message|instructions?|rules?)\b.{0,100}"
    r"\b(?:show|reveal|print|repeat|quote|display|export|dump|leak)\b"
    r"|\b(?:ignore|disregard|override|replace|modify|rewrite|disable|forget)\b"
    r".{0,100}\b(?:instructions?|prompts?|rules?)\b"
    r"|\b(?:you are now|from now on|new system prompt|developer mode|jailbreak)\b"
    r")", re.IGNORECASE | re.DOTALL,
)

TOPIC_REFUSAL = "I can't help with that restricted topic. Please ask me about a technical subject."
PROMPT_REFUSAL = "I can't reveal or change my internal instructions. I can discuss prompt engineering generally."


def check_user_message(message: str) -> tuple[bool, str]:
    """Return allowed and reason. Reject before any external service call."""
    if RESTRICTED.search(message):
        return False, TOPIC_REFUSAL
    if PROMPT_ATTACK.search(message):
        return False, PROMPT_REFUSAL
    return True, ""


def check_output(answer: str) -> str:
    """Second-layer filter for generated responses, not a proof of safety."""
    if RESTRICTED.search(answer):
        return TOPIC_REFUSAL
    if PROMPT_ATTACK.search(answer):
        return PROMPT_REFUSAL
    return answer
