from playwright.sync_api import Locator, Page
import logging
from scopus_bot.data.models import Document
from scopus_bot.core.scraping.row_extractor import ScopusRowExtractor

logger = logging.getLogger(__name__)

class ScopusResultsScraper:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.row_extractor = ScopusRowExtractor()

    def wait_for_results_table(self) -> bool:
        selectors = [
            "tr.TableItems-module__m0Z0b.TableItems-module__A6xTk",
            "table tbody tr",
            "tbody tr",
        ]

        for selector in selectors:
            try:
                self.page.locator(selector).first.wait_for(timeout=12_000)
                return True
            except Exception as exc:
                logger.debug("Selector falló en wait_for_results_table: %s", selector)
                continue

        return False

    def result_rows(self) -> Locator:
        primary = self.page.locator(
            "tr.TableItems-module__m0Z0b.TableItems-module__A6xTk"
        )
        if primary.count() > 0:
            return primary

        fallback = self.page.locator("table tbody tr")
        if fallback.count() > 0:
            return fallback

        return self.page.locator("tbody tr")

    def extract_current_page(self, document_type: str) -> list[Document]:
        documents: list[Document] = []

        if not self.wait_for_results_table():
            return documents

        rows = self.result_rows()
        total = rows.count()

        for index in range(total):
            row = rows.nth(index)

            try:
                document = self.row_extractor.extract(row, document_type)

                if document.title and document.title != "(sin titulo)":
                    documents.append(document)

            except Exception as exc:
                logger.warning(
                    "Error extrayendo fila %s: %s",
                    index,
                    str(exc),
                )
                continue

        return documents

    

    

    
