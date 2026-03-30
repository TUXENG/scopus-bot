from scopus_bot.core.scraping.normalizers import normalize_text
from scopus_bot.data.models import Document


def build_document_key(document: Document) -> str:
    if document.doi:
        return f"doi::{normalize_text(document.doi).lower()}"

    normalized_title = normalize_text(document.title).lower()[:200]
    normalized_year = str(document.year) if document.year is not None else "unknown"

    return f"title_year::{normalized_title}::{normalized_year}"


def deduplicate_documents(documents: list[Document]) -> list[Document]:
    unique_documents: list[Document] = []
    seen_keys: set[str] = set()

    for document in documents:
        key = build_document_key(document)

        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_documents.append(document)

    return unique_documents