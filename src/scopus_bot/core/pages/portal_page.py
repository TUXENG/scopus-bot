from playwright.sync_api import Page


class PortalPage:
    LOGIN_BUTTON = "#btnLogin"

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def wait_until_loaded(self) -> None:
        self.page.wait_for_selector(self.LOGIN_BUTTON, state="visible")

    def click_login(self) -> None:
        self.page.locator(self.LOGIN_BUTTON).click()