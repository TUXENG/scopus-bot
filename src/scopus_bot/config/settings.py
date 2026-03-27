from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path.cwd()
load_dotenv()


@dataclass(frozen=True)
class Settings:
    scopus_user: str
    scopus_password: str
    output_dir: Path
    logs_dir: Path
    headless: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            scopus_user=os.getenv("SCOPUS_USER", ""),
            scopus_password=os.getenv("SCOPUS_PASSWORD", ""),
            output_dir=BASE_DIR / "output",
            logs_dir=BASE_DIR / "logs",
            headless=os.getenv("SCOPUS_HEADLESS", "false").lower() == "true",
        )

    def ensure_directories(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings.from_env()
