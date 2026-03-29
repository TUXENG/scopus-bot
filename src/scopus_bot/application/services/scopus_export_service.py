from pathlib import Path

from scopus_bot.application.exporters.csv_exporter import CsvExporter


def export_documents_by_keyword(
    documents_by_keyword: dict[str, list],
    output_dir: Path,
    logger,
) -> None:
    exporter = CsvExporter()
    generated_files = exporter.export_documents_by_keyword(
        documents_by_keyword=documents_by_keyword,
        output_dir=output_dir,
    )

    for file_path in generated_files:
        logger.info("CSV generado: %s", file_path)