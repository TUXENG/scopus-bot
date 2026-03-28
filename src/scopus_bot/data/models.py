from dataclasses import dataclass, field
from datetime import datetime



@dataclass
class Document:
    title: str
    doc_type: str
    authors: str | None
    source: str | None
    year: int | None
    citations: int
    doi: str | None
    keyword: str | None = None


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



