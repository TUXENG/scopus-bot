from datetime import datetime

from scopus_bot.config.settings import settings
from scopus_bot.core.browser import create_browser_session
from scopus_bot.core.portal_page import PortalPage
from scopus_bot.core.login_page import LoginPage
from scopus_bot.core.extranet_page import ExtranetPage
from scopus_bot.core.library_resources_page import LibraryResourcesPage
from scopus_bot.core.scopus_page import ScopusPage
from scopus_bot.utils.logger import configure_logger
from scopus_bot.core.search_results_page import SearchResultsPage


def main() -> None:
    settings.ensure_directories()

    log_file = settings.logs_dir / f"scopus_bot_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = configure_logger(log_file)

    session = create_browser_session()

    try:
        portal = PortalPage(session.page)
        portal.open(settings.portal_url)
        logger.info("Portal cargado")

        portal.click_login()
        logger.info("Botón login pulsado")

        login = LoginPage(session.page)
        login.login(settings.scopus_user, settings.scopus_password)
        logger.info("Login enviado")

        extranet = ExtranetPage(session.page)
        extranet.wait_until_loaded()
        logger.info("Extranet cargada")

        resources_tab = extranet.open_library_resources_in_new_tab()
        logger.info("Recursos abiertos en nueva pestaña")

        resources_page = LibraryResourcesPage(resources_tab)
        resources_page.wait_until_loaded()
        logger.info("Página de recursos cargada")

        scopus_tab = resources_page.scroll_and_open_scopus_in_new_tab()
        logger.info("Scopus abierto en nueva pestaña")

        scopus_page = ScopusPage(scopus_tab)
        scopus_page.wait_until_loaded()
        logger.info("Scopus cargado")
        logger.info("URL Scopus: %s", scopus_page.current_url())
        logger.info("Título Scopus: %s", scopus_page.title())

        scopus_page.search("machine learning")
        logger.info("Búsqueda enviada")
        logger.info("Nueva URL: %s", scopus_page.current_url())
      
        results_page = SearchResultsPage(scopus_tab)
        results_page.wait_until_loaded()
        logger.info("Resultados cargados")
        logger.info("URL resultados: %s", results_page.current_url())
        logger.info("Título resultados: %s", results_page.title())

        results_page.prepare_results_view()
        logger.info("Resultados configurados: sort by cited by highest, display 200")
        input("Presiona Enter para cerrar...")

    finally:
        session.close()
        logger.info("Navegador cerrado")


if __name__ == "__main__":
    main()