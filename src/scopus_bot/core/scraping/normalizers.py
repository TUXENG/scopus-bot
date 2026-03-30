import re


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def normalize_optional_text(value: str | None) -> str | None:
    text = normalize_text(value)
    return text or None


def normalize_year(value: str | None) -> int | None:
    text = normalize_text(value)

    if not text:
        return None

    match = re.search(r"\b(19|20)\d{2}\b", text)
    return int(match.group(0)) if match else None


def normalize_url(value: str | None) -> str | None:
    text = normalize_text(value)

    if not text:
        return None

    if text.startswith(("http://", "https://")):
        return text

    if text.startswith("/"):
        return f"https://www.scopus.com{text}"

    return text