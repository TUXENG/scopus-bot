import re
from playwright.sync_api import Locator, Page

from scopus_bot.data.models import Document
import logging

logger = logging.getLogger(__name__)

class ScopusResultsScraper:
    def __init__(self, page: Page) -> None:
        self.page = page

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
                document = self.extract_row(row, document_type)

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

    def extract_row(self, row: Locator, document_type: str) -> Document:
        return Document(
            title=self._get_title(row),
            doc_type=document_type,
            authors=self._get_authors(row),
            source=self._get_source(row),
            year=self._get_year(row),
            citations=self._get_citations(row),
            doi=self._get_link(row),
        )

    def _get_title(self, row: Locator) -> str:
        selectors = [
            ("td.TableItems-module__UF1E0", "a.Button-module__f8gtt span.Button-module__Imdmt span"),
            ("td.TableItems-module__UF1E0", "h3 a span"),
            ("td.TableItems-module__UF1E0", "h3 a"),
            ("td.TableItems-module__UF1E0", "a"),
        ]

        for td_selector, child_selector in selectors:
            try:
                td = row.locator(td_selector).first
                if td.count() == 0:
                    continue

                element = td.locator(child_selector).first
                if element.count() == 0:
                    continue

                text = element.inner_text().strip()
                if text:
                    return re.sub(r"\s+", " ", text)
            except Exception as exc:
                logger.debug("Error en _get_title: %s", str(exc))
                continue

        return "(sin titulo)"

    def _get_authors(self, row: Locator) -> str:
        try:
            td = row.locator("td.TableItems-module__lmTQ0").first
            if td.count() == 0:
                return ""

            text = td.inner_text().strip()
            return re.sub(r"\s+", " ", text)
        except Exception:
            return ""

    def _get_source(self, row: Locator) -> str:
        selectors = [
            ("td.TableItems-module__zJIIe", "[data-component='document-source'] a span"),
            ("td.TableItems-module__zJIIe", "a span"),
            ("td.TableItems-module__zJIIe", "a"),
        ]

        for td_selector, child_selector in selectors:
            try:
                td = row.locator(td_selector).first
                if td.count() == 0:
                    continue

                element = td.locator(child_selector).first
                if element.count() == 0:
                    continue

                text = element.inner_text().strip()
                if text:
                    return re.sub(r"\s+", " ", text)
            except Exception:
                continue

        return ""

    def _get_year(self, row: Locator) -> str:
        selectors = [
            ("td.TableItems-module__472S1", "[data-testid='document-publication-year'] span"),
            ("td.TableItems-module__472S1", None),
        ]

        for td_selector, child_selector in selectors:
            try:
                td = row.locator(td_selector).first
                if td.count() == 0:
                    continue

                if child_selector is None:
                    text = td.inner_text().strip()
                else:
                    element = td.locator(child_selector).first
                    if element.count() == 0:
                        continue
                    text = element.inner_text().strip()

                if text:
                    return re.sub(r"\s+", " ", text)
            except Exception:
                continue

        return ""

    def _get_citations(self, row: Locator) -> int:
        selectors = [
            ("td.TableItems-module__hCBfh", "a span"),
            ("td.TableItems-module__hCBfh", "a"),
            ("td.TableItems-module__hCBfh", "span"),
        ]

        for td_selector, child_selector in selectors:
            try:
                td = row.locator(td_selector).first
                if td.count() == 0:
                    continue

                element = td.locator(child_selector).first
                if element.count() == 0:
                    continue

                text = element.inner_text().strip()
                return self._clean_number(text)
            except Exception:
                continue

        return 0

    def _get_link(self, row: Locator) -> str:
        selectors = [
            "td.TableItems-module__UF1E0 h3 a",
            "td.TableItems-module__UF1E0 a",
        ]

        for selector in selectors:
            try:
                anchor = row.locator(selector).first
                if anchor.count() == 0:
                    continue

                href = anchor.get_attribute("href")
                if not href:
                    continue

                href = href.strip()
                if href.startswith("http"):
                    return href

                return f"https://www.scopus.com{href}"
            except Exception:
                continue

        return ""

    def _clean_number(self, text: str) -> int:
        digits = re.sub(r"[^\d]", "", text or "")
        return int(digits) if digits else 0