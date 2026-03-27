from datetime import datetime

from scopus_bot.config.settings import settings
from scopus_bot.utils.logger import configure_logger


def main() -> None:
    settings.ensure_directories()

    log_file = settings.logs_dir / f"scopus_bot_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = configure_logger(log_file)

    logger.info("Scopus Bot iniciado")
    logger.info("Directorio de salida: %s", settings.output_dir)
    logger.info("Directorio de logs: %s", settings.logs_dir)


if __name__ == "__main__":
    main()
