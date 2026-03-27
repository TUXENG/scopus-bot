from playwright.sync_api import Page


class PortalPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def click_login(self) -> None:
        self.page.wait_for_selector("#btnLogin")
        self.page.click("#btnLogin")