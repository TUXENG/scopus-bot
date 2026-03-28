from datetime import datetime

from scopus_bot.config.filters import DOCUMENT_TYPE_TEST_IDS, SUBJECT_AREA_TEST_IDS, NUMS_PAGE
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

def scrape_all_pages_for_document_type(
    results_page: SearchResultsPage,
    scraper: ScopusResultsScraper,
    document_type_name: str,
    logger,
    max_pages: int = 10,
) -> list:
    documents = []
    current_page = 1

    while current_page <= max_pages:
        logger.info(
            "Extrayendo página %s para Document Type: %s",
            current_page,
            document_type_name,
        )

        page_documents = scraper.extract_current_page(document_type=document_type_name)
        logger.info(
            "Documentos extraídos en página %s para %s: %s",
            current_page,
            document_type_name,
            len(page_documents),
        )

        documents.extend(page_documents)

        if not results_page.has_next_page():
            logger.info(
                "No hay más páginas para Document Type: %s",
                document_type_name,
            )
            break

        moved = results_page.go_to_next_page()
        if not moved:
            logger.warning(
                "No se pudo avanzar a la siguiente página para Document Type: %s",
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
        scopus_page.search("machine learning")
        logger.info("Búsqueda enviada")
        logger.info("URL tras búsqueda: %s", scopus_page.current_url())

        # Results page
        results_page = SearchResultsPage(scopus_tab)
        results_page.wait_until_loaded()
        logger.info("Resultados cargados")
        logger.info("URL resultados: %s", results_page.current_url())
        logger.info("Título resultados: %s", results_page.title())

        # Results configuration
        results_page.prepare_results_view()
        logger.info("Resultados configurados: sort by cited by highest, display 200")

        # Subject area filter
        subject_filter = SubjectAreaFilter(scopus_tab)
        subject_area_result = subject_filter.apply_limit(SUBJECT_AREA_TEST_IDS)

        logger.info(
            "Subject areas aplicadas: %s",
            ", ".join(subject_area_result["selected"]),
        )

        if subject_area_result["selected"]:
            subject_filter.validate_applied(subject_area_result["selected"])

        if subject_area_result["missing"]:
            logger.warning(
                "Subject areas no encontradas: %s",
                ", ".join(subject_area_result["missing"]),
            )

        # Document type filter - prueba con un tipo
        document_type_filter = DocumentTypeFilter(scopus_tab)
        scraper = ScopusResultsScraper(scopus_tab)

        document_type_names = [
            "Article",
            "Review",
            "Conference paper",
        ]

        all_documents = []

        for document_type_name in document_type_names:
            logger.info("Iniciando extracción para Document Type: %s", document_type_name)

            test_id = DOCUMENT_TYPE_TEST_IDS.get(document_type_name)
            if not test_id:
                logger.warning(
                    "No existe test id configurado para Document Type: %s",
                    document_type_name,
                )
                continue

            document_type_filter.reset_and_apply(test_id)
            logger.info("Filtro Document Type aplicado: %s", document_type_name)

            document_type_filter.validate_applied(document_type_name)
            results_page.go_to_first_page()
            
            documents = scrape_all_pages_for_document_type(
                results_page=results_page,
                scraper=scraper,
                document_type_name=document_type_name,
                logger=logger,
                max_pages=NUMS_PAGE,
            )
            logger.info(
                "Documentos extraídos para %s en todas las páginas: %s",
                document_type_name,
                len(documents),
            )

            all_documents.extend(documents)

        logger.info("Total acumulado de documentos antes de deduplicar: %s", len(all_documents))
        unique_documents = deduplicate_documents(all_documents)
        logger.info("Total de documentos después de deduplicar: %s", len(unique_documents))


        input("Presiona Enter para cerrar...")

    finally:
        session.close()
        logger.info("Navegador cerrado")