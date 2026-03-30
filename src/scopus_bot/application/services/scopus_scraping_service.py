from scopus_bot.config.keywords import KEYWORDS
from scopus_bot.config.filters import (
    DOCUMENT_TYPE_TEST_IDS,
    SUBJECT_AREA_TEST_IDS,
    NUM_PAGES,
    FILTER_YEAR_TO,
    DOCUMENT_TYPE_NAMES,
)
from scopus_bot.core.filters.document_type_filter import DocumentTypeFilter
from scopus_bot.core.filters.subject_area_filter import SubjectAreaFilter
from scopus_bot.core.pages.scopus_page import ScopusPage
from scopus_bot.core.pages.search_results_page import SearchResultsPage
from scopus_bot.core.scraping.deduplicator import deduplicate_documents
from scopus_bot.core.scraping.scopus_results_scraper import ScopusResultsScraper
from scopus_bot.data.models import Document



def scrape_documents_by_keyword(scopus_tab, logger) -> dict[str, list[Document]]:
    scopus_page = ScopusPage(scopus_tab)
    results_page = SearchResultsPage(scopus_tab)
    document_type_filter = DocumentTypeFilter(scopus_tab)
    scraper = ScopusResultsScraper(scopus_tab)

    documents_by_keyword: dict[str, list[Document]] = {}
    all_documents: list[Document] = []

    for keyword in KEYWORDS:
        keyword_documents = _scrape_single_keyword(
            keyword=keyword,
            scopus_page=scopus_page,
            results_page=results_page,
            document_type_filter=document_type_filter,
            scraper=scraper,
            logger=logger,
        )

        unique_keyword_documents = deduplicate_documents(keyword_documents)
        documents_by_keyword[keyword] = unique_keyword_documents

        logger.info(
            "Total de documentos para keyword '%s' después de deduplicar: %s",
            keyword,
            len(unique_keyword_documents),
        )

        all_documents.extend(unique_keyword_documents)

    logger.info(
        "Total acumulado de documentos antes de deduplicar globalmente: %s",
        len(all_documents),
    )

    unique_documents = deduplicate_documents(all_documents)

    logger.info(
        "Total de documentos después de deduplicar globalmente: %s",
        len(unique_documents),
    )

    return documents_by_keyword


def _scrape_single_keyword(
    keyword: str,
    scopus_page: ScopusPage,
    results_page: SearchResultsPage,
    document_type_filter: DocumentTypeFilter,
    scraper: ScopusResultsScraper,
    logger,
) -> list[Document]:
    logger.info("Iniciando scraping para keyword: %s", keyword)

    scopus_page.search(keyword)
    logger.info("Búsqueda enviada para keyword: %s", keyword)

    results_page.wait_until_loaded()
    logger.info("Resultados cargados para keyword: %s", keyword)
    logger.info("URL resultados: %s", results_page.current_url())
    logger.info("Título resultados: %s", results_page.title())

    results_page.prepare_results_view()
    logger.info(
        "Resultados configurados para keyword '%s': sort by cited by highest, display 200",
        keyword,
    )

    results_page.set_year_to(FILTER_YEAR_TO)
    logger.info("Filtro de año TO aplicado para keyword '%s': %s", keyword, FILTER_YEAR_TO)

    _apply_subject_area_filter(page=scopus_page.page, keyword=keyword, logger=logger)

    keyword_documents: list[Document] = []

    for document_type_name in DOCUMENT_TYPE_NAMES:
        documents = _scrape_single_document_type(
            results_page=results_page,
            scraper=scraper,
            document_type_filter=document_type_filter,
            document_type_name=document_type_name,
            keyword=keyword,
            logger=logger,
        )
        keyword_documents.extend(documents)

    results_page.scroll_to_top()
    logger.info("Scraping finalizado para keyword: %s", keyword)

    return keyword_documents


def _apply_subject_area_filter(page, keyword: str, logger) -> None:
    subject_filter = SubjectAreaFilter(page)
    subject_area_result = subject_filter.apply_limit(SUBJECT_AREA_TEST_IDS)

    logger.info(
        "Subject areas aplicadas para keyword '%s': %s",
        keyword,
        ", ".join(subject_area_result["selected"]),
    )

    if subject_area_result["selected"]:
        subject_filter.validate_applied(subject_area_result["selected"])

    if subject_area_result["missing"]:
        logger.warning(
            "Subject areas no encontradas para keyword '%s': %s",
            keyword,
            ", ".join(subject_area_result["missing"]),
        )


def _scrape_single_document_type(
    results_page: SearchResultsPage,
    scraper: ScopusResultsScraper,
    document_type_filter: DocumentTypeFilter,
    document_type_name: str,
    keyword: str,
    logger,
) -> list[Document]:
    logger.info(
        "Iniciando extracción para keyword '%s' y Document Type: %s",
        keyword,
        document_type_name,
    )

    test_id = DOCUMENT_TYPE_TEST_IDS.get(document_type_name)
    if not test_id:
        logger.warning(
            "No existe test id configurado para Document Type: %s",
            document_type_name,
        )
        return []

    document_type_filter.reset_and_apply(test_id)
    logger.info(
        "Filtro Document Type aplicado para keyword '%s': %s",
        keyword,
        document_type_name,
    )

    document_type_filter.validate_applied(document_type_name)
    results_page.go_to_first_page()

    documents = _scrape_all_pages_for_document_type(
        results_page=results_page,
        scraper=scraper,
        document_type_name=document_type_name,
        logger=logger,
        keyword=keyword,
        max_pages=NUM_PAGES,
    )

    logger.info(
        "Documentos extraídos para keyword '%s' y %s: %s",
        keyword,
        document_type_name,
        len(documents),
    )

    return documents


def _scrape_all_pages_for_document_type(
    results_page: SearchResultsPage,
    scraper: ScopusResultsScraper,
    document_type_name: str,
    logger,
    keyword: str,
    max_pages: int = 10,
) -> list[Document]:
    documents: list[Document] = []
    current_page = 1

    while current_page <= max_pages:
        logger.info(
            "Extrayendo página %s para keyword '%s' y Document Type: %s",
            current_page,
            keyword,
            document_type_name,
        )

        page_documents = scraper.extract_current_page(
            document_type=document_type_name,
        )

        logger.info(
            "Documentos extraídos en página %s para keyword '%s' y %s: %s",
            current_page,
            keyword,
            document_type_name,
            len(page_documents),
        )

        documents.extend(page_documents)

        if not results_page.has_next_page():
            logger.info(
                "No hay más páginas para keyword '%s' y Document Type: %s",
                keyword,
                document_type_name,
            )
            break

        moved = results_page.go_to_next_page()
        if not moved:
            logger.warning(
                "No se pudo avanzar a la siguiente página para keyword '%s' y Document Type: %s",
                keyword,
                document_type_name,
            )
            break

        current_page += 1

    return documents