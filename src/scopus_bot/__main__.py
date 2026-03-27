from datetime import datetime

from scopus_bot.config.settings import settings
from scopus_bot.core.browser import create_browser_session
from scopus_bot.core.portal_page import PortalPage
from scopus_bot.core.login_page import LoginPage
from scopus_bot.core.extranet_page import ExtranetPage
from scopus_bot.utils.logger import configure_logger


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
        logger.info("Botón de login pulsado")

        login = LoginPage(session.page)
        login.login(settings.scopus_user, settings.scopus_password)
        logger.info("Login enviado")

        extranet = ExtranetPage(session.page)
        extranet.wait_until_loaded()
        logger.info("Extranet cargada")

        extranet.open_library_resources()
        logger.info("Botón de recursos pulsado")
         
        input("enter para cerrar")


    finally:
        session.close()
        logger.info("Navegador cerrado")


if __name__ == "__main__":
    main()