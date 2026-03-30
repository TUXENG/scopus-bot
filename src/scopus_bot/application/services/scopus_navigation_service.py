from scopus_bot.config.settings import settings
from scopus_bot.core.pages.extranet_page import ExtranetPage
from scopus_bot.core.pages.library_resources_page import LibraryResourcesPage
from scopus_bot.core.pages.login_page import LoginPage
from scopus_bot.core.pages.portal_login_page import PortalLoginPage
from scopus_bot.core.pages.portal_page import PortalPage
from scopus_bot.core.pages.scopus_page import ScopusPage


def open_scopus_tab(session, logger):
    # 1. Portal
    portal = PortalPage(session.page)
    portal.open(settings.portal_url)
    portal.wait_until_loaded()
    logger.info("Portal cargado")

    portal.click_login()
    logger.info("Botón login pulsado")

    # 2. Login portal
    portal_login = PortalLoginPage(session.page)
    portal_login.login(
        settings.portal_user,
        settings.portal_password,
    )
    logger.info("Login portal completado")

    # 3. Extranet
    extranet = ExtranetPage(session.page)
    extranet.wait_until_loaded()
    logger.info("Extranet cargada")

    # 4. Recursos
    resources_tab = extranet.open_library_resources_in_new_tab()
    logger.info("Recursos abiertos en nueva pestaña")

    resources_page = LibraryResourcesPage(resources_tab)
    resources_page.wait_until_loaded()
    logger.info("Página de recursos cargada")

    # 5. Scopus
    scopus_tab = resources_page.open_scopus()
    logger.info("Scopus abierto en nueva pestaña")

    scopus_page = ScopusPage(scopus_tab)
    scopus_page.wait_until_loaded()
    logger.info("Scopus cargado")

    # 6. Login Scopus
    scopus_page.click_sign_in()
    scopus_page.click_institution_login()

    login_page = LoginPage(scopus_tab)
    login_page.login(
        settings.scopus_user,
        settings.scopus_password,
    )
    logger.info("Login Scopus completado")

    scopus_page.wait_until_ready_for_search()

    logger.info("URL Scopus: %s", scopus_page.current_url())
    logger.info("Título Scopus: %s", scopus_page.title())

    return scopus_tab