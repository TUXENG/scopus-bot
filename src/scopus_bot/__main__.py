from datetime import datetime

from scopus_bot.config.settings import settings
from scopus_bot.core.browser import create_browser_session
from scopus_bot.core.portal_page import PortalPage
from scopus_bot.core.login_page import LoginPage
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
        logger.info("Botón login pulsado")

        login = LoginPage(session.page)
        login.login(settings.scopus_user, settings.scopus_password)

        logger.info("Login enviado")
        

    finally:
        session.page.wait_for_timeout(10000)
        session.close()
        logger.info("Navegador cerrado")


if __name__ == "__main__":
    main()