import re


BIAS_TERMS = [
    "male",
    "female",
    "married",
    "single",
    "date of birth",
    "dob",
    "religion",
    "nationality",
]


def clean_text(text: str) -> str:
    if not text:
        return ""
    value = text.replace("\x00", " ")
    value = re.sub(r"\r", "\n", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def remove_bias_terms(text: str) -> str:
    cleaned = text or ""
    for term in BIAS_TERMS:
        cleaned = re.sub(term, " ", cleaned, flags=re.IGNORECASE)
    return clean_text(cleaned)
