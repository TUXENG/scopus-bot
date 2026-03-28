import logging
import re

from playwright.sync_api import Locator

from scopus_bot.core.scraping.normalizers import (
    normalize_optional_text,
    normalize_text,
    normalize_url,
    normalize_year,
)
from scopus_bot.data.models import Document

logger = logging.getLogger(__name__)


class ScopusRowExtractor:
    def extract(
        self,
        row: Locator,
        document_type: str,
        keyword: str | None = None,
    ) -> Document:
        title = normalize_text(self._get_title(row))
        authors = normalize_optional_text(self._get_authors(row))
        source = normalize_optional_text(self._get_source(row))
        year = normalize_year(self._get_year(row))
        doi = normalize_url(self._get_link(row))

        return Document(
            title=title,
            doc_type=normalize_text(document_type),
            authors=authors,
            source=source,
            year=year,
            citations=self._get_citations(row),
            doi=doi,
            keyword=normalize_text(keyword) if keyword else None,
        )

    def _get_title(self, row: Locator) -> str:
        selectors = [
            (
                "td.TableItems-module__UF1E0",
                "a.Button-module__f8gtt span.Button-module__Imdmt span",
            ),
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
                    return text
            except Exception as exc:
                logger.debug("Error en _get_title: %s", str(exc))
                continue

        return "(sin titulo)"

    def _get_authors(self, row: Locator) -> str:
        try:
            td = row.locator("td.TableItems-module__lmTQ0").first
            if td.count() == 0:
                return ""

            return td.inner_text().strip()
        except Exception as exc:
            logger.debug("Error en _get_authors: %s", str(exc))
            return ""

    def _get_source(self, row: Locator) -> str:
        selectors = [
            (
                "td.TableItems-module__zJIIe",
                "[data-component='document-source'] a span",
            ),
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
                    return text
            except Exception as exc:
                logger.debug("Error en _get_source: %s", str(exc))
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
                    return text
            except Exception as exc:
                logger.debug("Error en _get_year: %s", str(exc))
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
            except Exception as exc:
                logger.debug("Error en _get_citations: %s", str(exc))
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

                return href.strip()
            except Exception as exc:
                logger.debug("Error en _get_link: %s", str(exc))
                continue

        return ""

    def _clean_number(self, text: str) -> int:
        digits = re.sub(r"[^\d]", "", text or "")
        return int(digits) if digits else 0