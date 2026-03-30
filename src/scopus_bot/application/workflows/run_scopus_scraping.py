from datetime import datetime

from scopus_bot.config.settings import settings
from scopus_bot.core.browser.session import create_browser_session
from scopus_bot.utils.logger import configure_logger

from scopus_bot.application.services.scopus_navigation_service import (
    open_scopus_tab,
)
from scopus_bot.application.services.scopus_scraping_service import (
    scrape_documents_by_keyword,
)
from scopus_bot.application.services.scopus_export_service import (
    export_documents_by_keyword,
)


def run() -> None:
    settings.ensure_directories()

    log_file = settings.logs_dir / f"scopus_bot_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = configure_logger(log_file)

    session = create_browser_session()

    try:
        scopus_tab = open_scopus_tab(session=session, logger=logger)

        documents_by_keyword = scrape_documents_by_keyword(
            scopus_tab=scopus_tab,
            logger=logger,
        )

        output_dir = settings.output_dir / "csv"
        export_documents_by_keyword(
            documents_by_keyword=documents_by_keyword,
            output_dir=output_dir,
            logger=logger,
        )

    finally:
        session.close()
        logger.info("Navegador cerrado")