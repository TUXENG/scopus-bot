from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path.cwd()
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class Settings:
    scopus_user: str
    scopus_password: str
    portal_url: str
    headless: bool
    output_dir: Path
    logs_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        user = os.getenv("PORTAL_USER")
        password = os.getenv("PORTAL_PASSWORD")
        portal_url = os.getenv("PORTAL_URL")

        if not user or not password or not portal_url:
            raise ValueError(
                "Faltan variables: SCOPUS_USER, SCOPUS_PASSWORD o PORTAL_URL"
            )

        return cls(
            scopus_user=user,
            scopus_password=password,
            portal_url=portal_url,
            headless=os.getenv("SCOPUS_HEADLESS", "false").lower() == "true",
            output_dir=BASE_DIR / "output",
            logs_dir=BASE_DIR / "logs",
        )

    def ensure_directories(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings.from_env()