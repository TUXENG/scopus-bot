from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path.cwd()
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class Settings:
    portal_user: str
    portal_password: str

    scopus_user: str
    scopus_password: str

    portal_url: str

    headless: bool
    output_dir: Path
    logs_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        portal_user = os.getenv("PORTAL_USER")
        portal_password = os.getenv("PORTAL_PASSWORD")

        scopus_user = os.getenv("SCOPUS_USER")
        scopus_password = os.getenv("SCOPUS_PASSWORD")

        portal_url = os.getenv("PORTAL_URL")

        missing = [
            name
            for name, value in {
                "PORTAL_USER": portal_user,
                "PORTAL_PASSWORD": portal_password,
                "SCOPUS_USER": scopus_user,
                "SCOPUS_PASSWORD": scopus_password,
                "PORTAL_URL": portal_url,
            }.items()
            if not value
        ]

        if missing:
            raise ValueError(f"Faltan variables de entorno: {', '.join(missing)}")

        return cls(
            portal_user=portal_user,
            portal_password=portal_password,
            scopus_user=scopus_user,
            scopus_password=scopus_password,
            portal_url=portal_url,
            headless=os.getenv("SCOPUS_HEADLESS", "false").lower() == "true",
            output_dir=BASE_DIR / "output",
            logs_dir=BASE_DIR / "logs",
        )

    def ensure_directories(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings.from_env()