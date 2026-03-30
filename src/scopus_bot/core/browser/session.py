from dataclasses import dataclass

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from scopus_bot.config.settings import settings


@dataclass
class BrowserSession:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page

    def close(self) -> None:
        try:
            self.context.close()
        finally:
            try:
                self.browser.close()
            finally:
                self.playwright.stop()


def create_browser_session() -> BrowserSession:
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(
        headless=settings.headless,
    )

    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
    )

    page = context.new_page()
    page.set_default_timeout(10_000)
    page.set_default_navigation_timeout(20_000)

    return BrowserSession(
        playwright=playwright,
        browser=browser,
        context=context,
        page=page,
    )