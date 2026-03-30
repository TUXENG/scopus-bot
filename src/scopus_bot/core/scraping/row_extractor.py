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
    def extract(self, row: Locator, document_type: str) -> Document:
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
        )

    def _get_title(self, row: Locator) -> str:
        text = self._extract_text(
            row,
            [
                ("td.TableItems-module__UF1E0", "a.Button-module__f8gtt span.Button-module__Imdmt span"),
                ("td.TableItems-module__UF1E0", "h3 a span"),
                ("td.TableItems-module__UF1E0", "h3 a"),
                ("td.TableItems-module__UF1E0", "a"),
            ],
            field_name="title",
        )
        return text or "(sin titulo)"

    def _get_authors(self, row: Locator) -> str:
        text = self._extract_text(
            row,
            [
                ("td.TableItems-module__lmTQ0", None),
            ],
            field_name="authors",
        )
        return text or ""

    def _get_source(self, row: Locator) -> str:
        text = self._extract_text(
            row,
            [
                ("td.TableItems-module__zJIIe", "[data-component='document-source'] a span"),
                ("td.TableItems-module__zJIIe", "a span"),
                ("td.TableItems-module__zJIIe", "a"),
            ],
            field_name="source",
        )
        return text or ""

    def _get_year(self, row: Locator) -> str:
        text = self._extract_text(
            row,
            [
                ("td.TableItems-module__472S1", "[data-testid='document-publication-year'] span"),
                ("td.TableItems-module__472S1", None),
            ],
            field_name="year",
        )
        return text or ""

    def _get_citations(self, row: Locator) -> int:
        text = self._extract_text(
            row,
            [
                ("td.TableItems-module__hCBfh", "a span"),
                ("td.TableItems-module__hCBfh", "a"),
                ("td.TableItems-module__hCBfh", "span"),
            ],
            field_name="citations",
        )
        return self._clean_number(text)

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
                logger.debug("Error en _get_link con selector '%s': %s", selector, str(exc))
                continue

        return ""

    def _extract_text(
        self,
        row: Locator,
        selectors: list[tuple[str, str | None]],
        field_name: str,
    ) -> str:
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
                logger.debug(
                    "Error extrayendo %s con selector td='%s' child='%s': %s",
                    field_name,
                    td_selector,
                    child_selector,
                    str(exc),
                )
                continue

        return ""

    def _clean_number(self, text: str) -> int:
        digits = re.sub(r"[^\d]", "", text or "")
        return int(digits) if digits else 0