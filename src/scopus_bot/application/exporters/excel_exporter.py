from pathlib import Path
import csv

from scopus_bot.data.models import Document


class CsvExporter:
    HEADERS = [
        "Title",
        "Document Type",
        "Authors",
        "Source",
        "Year",
        "Citations",
        "DOI / Link",
    ]

    def export_documents_by_keyword(
        self,
        documents_by_keyword: dict[str, list[Document]],
        output_dir: Path,
    ) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        for keyword, documents in documents_by_keyword.items():
            file_name = self._build_file_name(keyword)
            file_path = output_dir / file_name

            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                writer.writerow(self.HEADERS)

                for document in documents:
                    writer.writerow(
                        [
                            document.title,
                            document.doc_type,
                            document.authors,
                            document.source,
                            document.year,
                            document.citations,
                            document.doi,
                        ]
                    )

            generated_files.append(file_path)

        return generated_files

    def _build_file_name(self, keyword: str) -> str:
        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']', ' ']

        name = keyword.strip() or "sin_keyword"

        for char in invalid_chars:
            name = name.replace(char, "_")

        return f"{name[:50]}.csv"