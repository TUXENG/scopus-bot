import re


def normalize_text(value: str | None) -> str:
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def normalize_optional_text(value: str | None) -> str | None:
    normalized = normalize_text(value)
    return normalized or None


def normalize_year(value: str | None) -> int | None:
    normalized = normalize_text(value)

    if not normalized:
        return None

    match = re.search(r"\b(19|20)\d{2}\b", normalized)
    if not match:
        return None

    return int(match.group(0))


def normalize_url(value: str | None) -> str | None:
    normalized = normalize_text(value)

    if not normalized:
        return None

    if normalized.startswith("http://") or normalized.startswith("https://"):
        return normalized

    if normalized.startswith("/"):
        return f"https://www.scopus.com{normalized}"

    return normalized