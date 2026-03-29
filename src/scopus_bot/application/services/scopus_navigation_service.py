from scopus_bot.config.settings import settings
from scopus_bot.core.pages.extranet_page import ExtranetPage
from scopus_bot.core.pages.library_resources_page import LibraryResourcesPage
from scopus_bot.core.pages.login_page import LoginPage
from scopus_bot.core.pages.portal_page import PortalPage
from scopus_bot.core.pages.scopus_page import ScopusPage


def open_scopus_tab(session, logger):
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

    return scopus_tab
