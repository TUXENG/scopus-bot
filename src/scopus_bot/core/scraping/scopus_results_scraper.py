import logging

from playwright.sync_api import Locator, Page

from scopus_bot.core.scraping.row_extractor import ScopusRowExtractor
from scopus_bot.data.models import Document

logger = logging.getLogger(__name__)


class ScopusResultsScraper:
    ROW_SELECTORS = [
        "tr.TableItems-module__m0Z0b.TableItems-module__A6xTk",
        "table tbody tr",
        "tbody tr",
    ]

    def __init__(self, page: Page) -> None:
        self.page = page
        self.row_extractor = ScopusRowExtractor()

    def wait_for_results_table(self) -> bool:
        for selector in self.ROW_SELECTORS:
            try:
                self.page.locator(selector).first.wait_for(state="visible", timeout=12_000)
                return True
            except Exception:
                logger.debug("Selector falló en wait_for_results_table: %s", selector)
                continue

        logger.warning("No se encontró tabla de resultados en la página actual")
        return False

    def result_rows(self) -> Locator:
        for selector in self.ROW_SELECTORS:
            locator = self.page.locator(selector)
            try:
                if locator.count() > 0:
                    return locator
            except Exception:
                continue

        return self.page.locator("tbody tr")

    def extract_current_page(self, document_type: str) -> list[Document]:
        documents: list[Document] = []

        if not self.wait_for_results_table():
            return documents

        rows = self.result_rows()
        total = rows.count()

        logger.info("Filas detectadas en la página actual: %s", total)

        for index in range(total):
            row = rows.nth(index)

            try:
                document = self.row_extractor.extract(row, document_type)

                if document.title and document.title != "(sin titulo)":
                    documents.append(document)
                else:
                    logger.debug("Fila %s descartada por no tener título válido", index)

            except Exception as exc:
                logger.warning("Error extrayendo fila %s: %s", index, str(exc))
                continue

        logger.info("Documentos válidos extraídos en la página actual: %s", len(documents))
        return documents