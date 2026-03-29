from playwright.sync_api import Page


class LibraryResourcesPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

    def scroll_until_scopus_visible(self, max_scrolls: int = 12) -> None:
        scopus_card = self.page.locator("text=Scopus").first

        for _ in range(max_scrolls):
            if scopus_card.is_visible():
                return
            self.page.mouse.wheel(0, 1200)
            self.page.wait_for_timeout(500)

        raise RuntimeError("No se encontró la card de Scopus después de hacer scroll")

    def open_scopus(self) -> None:
        scopus_card = self.page.locator("text=Scopus").first
        scopus_card.wait_for()
        scopus_card.click()

    def scroll_and_open_scopus(self) -> None:
        self.scroll_until_scopus_visible()
        self.open_scopus()