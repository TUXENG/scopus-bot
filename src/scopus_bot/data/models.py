from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Document:
    title: str = ""
    doc_type: str = ""
    authors: str = ""
    source: str = ""
    year: str = ""
    citations: int = 0
    doi: str = ""


@dataclass
class SearchResult:
    keyword: str
    documents: list[Document] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    total_pages: int = 0
    success: bool = False
    error: str | None = None

    @property
    def total_documents(self) -> int:
        return len(self.documents)

