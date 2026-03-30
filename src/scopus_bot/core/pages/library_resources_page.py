from playwright.sync_api import Page


class LibraryResourcesPage:
    SCOPUS_CARD = "text=Scopus"

    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

    def scroll_until_scopus_visible(self) -> None:
        scopus_card = self.page.locator(self.SCOPUS_CARD).first

        try:
            scopus_card.scroll_into_view_if_needed()
            scopus_card.wait_for(state="visible", timeout=10_000)
        except Exception:
            raise RuntimeError("No se encontró la card de Scopus")

    def open_scopus_in_new_tab(self) -> Page:
        scopus_card = self.page.locator(self.SCOPUS_CARD).first
        scopus_card.wait_for(state="visible")

        with self.page.context.expect_page() as new_page_info:
            scopus_card.click()

        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        return new_page

    def open_scopus(self) -> Page:
        self.scroll_until_scopus_visible()
        return self.open_scopus_in_new_tab()