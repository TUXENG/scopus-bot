from dataclasses import dataclass

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from scopus_bot.config.settings import settings


@dataclass
class BrowserSession:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page

    def close(self) -> None:
        self.context.close()
        self.browser.close()
        self.playwright.stop()


def create_browser_session() -> BrowserSession:
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=settings.headless)
    context = browser.new_context()
    page = context.new_page()

    return BrowserSession(
        playwright=playwright,
        browser=browser,
        context=context,
        page=page,
    )