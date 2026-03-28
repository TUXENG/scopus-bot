from datetime import datetime

from scopus_bot.config.settings import settings
from scopus_bot.core.browser.session import create_browser_session
from scopus_bot.core.filters.document_type_filter import DocumentTypeFilter
from scopus_bot.core.filters.subject_area_filter import SubjectAreaFilter
from scopus_bot.core.pages.extranet_page import ExtranetPage
from scopus_bot.core.pages.library_resources_page import LibraryResourcesPage
from scopus_bot.core.pages.login_page import LoginPage
from scopus_bot.core.pages.portal_page import PortalPage
from scopus_bot.core.pages.scopus_page import ScopusPage
from scopus_bot.core.pages.search_results_page import SearchResultsPage
from scopus_bot.core.scraping.scopus_results_scraper import ScopusResultsScraper
from scopus_bot.utils.logger import configure_logger
from scopus_bot.core.scraping.deduplicator import deduplicate_documents
from scopus_bot.application.exporters.excel_exporter import ExcelExporter
from scopus_bot.config.keywords import KEYWORDS
from scopus_bot.config.filters import (
    DOCUMENT_TYPE_TEST_IDS, 
    SUBJECT_AREA_TEST_IDS, 
    NUMS_PAGE, 
    FILTER_YEAR_TO 
)

def scrape_all_pages_for_document_type(
    results_page: SearchResultsPage,
    scraper: ScopusResultsScraper,
    document_type_name: str,
    logger,
    keyword: str,
    max_pages: int = 10,
) -> list:
    documents = []
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
            keyword=keyword,
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

def run() -> None:
    settings.ensure_directories()

    log_file = settings.logs_dir / f"scopus_bot_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = configure_logger(log_file)

    session = create_browser_session()

    try:
        # Portal
        portal = PortalPage(session.page)
        portal.open(settings.portal_url)
        logger.info("Portal cargado")

        portal.click_login()
        logger.info("Botón login pulsado")

        # Login
        login = LoginPage(session.page)
        login.login(settings.scopus_user, settings.scopus_password)
        logger.info("Login enviado")

        # Extranet
        extranet = ExtranetPage(session.page)
        extranet.wait_until_loaded()
        logger.info("Extranet cargada")

        resources_tab = extranet.open_library_resources_in_new_tab()
        logger.info("Recursos abiertos en nueva pestaña")

        # Resources page
        resources_page = LibraryResourcesPage(resources_tab)
        resources_page.wait_until_loaded()
        logger.info("Página de recursos cargada")

        scopus_tab = resources_page.scroll_and_open_scopus_in_new_tab()
        logger.info("Scopus abierto en nueva pestaña")

        # Scopus home
        scopus_page = ScopusPage(scopus_tab)
        scopus_page.wait_until_loaded()
        logger.info("Scopus cargado")
        logger.info("URL Scopus: %s", scopus_page.current_url())
        logger.info("Título Scopus: %s", scopus_page.title())

        # Search
        document_type_filter = DocumentTypeFilter(scopus_tab)
        scraper = ScopusResultsScraper(scopus_tab)

        document_type_names = [
            "Article",
            "Review",
            "Conference paper",
        ]

        all_documents = []
        documents_by_keyword: dict[str, list] = {}

        for index, keyword in enumerate(KEYWORDS):
            logger.info("Iniciando búsqueda para keyword: %s", keyword)
            
            if index == 0:
                scopus_page.search(keyword)
                logger.info("Búsqueda enviada desde Scopus home para keyword: %s", keyword)
            else:
                results_page = SearchResultsPage(scopus_tab)
                results_page.search(keyword)
                logger.info("Búsqueda enviada desde results page para keyword: %s", keyword)

            keyword_documents = []

            # 🔎 SEARCH
            scopus_page.search(keyword)
            logger.info("Búsqueda enviada para keyword: %s", keyword)
            logger.info("URL tras búsqueda: %s", scopus_page.current_url())

            # 📄 RESULTS PAGE
            results_page = SearchResultsPage(scopus_tab)
            results_page.wait_until_loaded()
            logger.info("Resultados cargados para keyword: %s", keyword)
            logger.info("URL resultados: %s", results_page.current_url())
            logger.info("Título resultados: %s", results_page.title())

            # ⚙️ CONFIGURAR RESULTADOS
            results_page.prepare_results_view()
            logger.info(
                "Resultados configurados para keyword '%s': sort by cited by highest, display 200",
                keyword,
            )

            # Filtro de año
            results_page.set_year_to(FILTER_YEAR_TO)
            logger.info("Filtro de año TO aplicado: 2024")

            # 🎯 SUBJECT AREA
            subject_filter = SubjectAreaFilter(scopus_tab)
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

            # 🔁 LOOP POR DOCUMENT TYPE
            for document_type_name in document_type_names:
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
                    continue

                document_type_filter.reset_and_apply(test_id)
                logger.info(
                    "Filtro Document Type aplicado para keyword '%s': %s",
                    keyword,
                    document_type_name,
                )

                document_type_filter.validate_applied(document_type_name)

                # 🔄 IMPORTANTE: volver a página 1
                results_page.go_to_first_page()

                # 📚 PAGINACIÓN
                documents = scrape_all_pages_for_document_type(
                    results_page=results_page,
                    scraper=scraper,
                    document_type_name=document_type_name,
                    logger=logger,
                    keyword=keyword,
                    max_pages=NUMS_PAGE,
                )

                logger.info(
                    "Documentos extraídos para keyword '%s' y %s: %s",
                    keyword,
                    document_type_name,
                    len(documents),
                )

                keyword_documents.extend(documents)
                all_documents.extend(documents)

            # 🧹 DEDUPLICACIÓN POR KEYWORD
            unique_keyword_documents = deduplicate_documents(keyword_documents)
            documents_by_keyword[keyword] = unique_keyword_documents

            logger.info(
                "Total de documentos para keyword '%s' después de deduplicar: %s",
                keyword,
                len(unique_keyword_documents),
            )

        # 🧹 DEDUPLICACIÓN GLOBAL
        logger.info("Total acumulado de documentos antes de deduplicar: %s", len(all_documents))

        unique_documents = deduplicate_documents(all_documents)

        logger.info("Total de documentos después de deduplicar: %s", len(unique_documents))

        # 📊 EXPORTAR A EXCEL (POR HOJAS)
        exporter = ExcelExporter()
        output_file = settings.output_dir / "scopus_results.xlsx"
        exporter.export_documents_by_keyword(documents_by_keyword, output_file)

        logger.info("Excel generado en: %s", output_file)

        input("Presiona Enter para cerrar...")

    finally:
        session.close()
        logger.info("Navegador cerrado")