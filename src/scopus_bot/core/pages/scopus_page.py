from playwright.sync_api import Page


class ScopusPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def current_url(self) -> str:
        return self.page.url

    def title(self) -> str:
        return self.page.title()

    def fill_search_query(self, query: str) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

        candidates = [
            self.page.get_by_role("textbox").first,
            self.page.locator('input[type="search"]:visible').first,
            self.page.locator('input[placeholder*="Search" i]:visible').first,
            self.page.locator('input[aria-label*="search" i]:visible').first,
            self.page.locator('input[name*="query" i]:visible').first,
            self.page.locator("input:visible").first,
            self.page.locator("textarea:visible").first,
        ]

        search_input = None

        for locator in candidates:
            try:
                if locator.count() == 0:
                    continue

                locator.scroll_into_view_if_needed()
                locator.wait_for(state="visible", timeout=5000)
                search_input = locator
                break
            except Exception:
                continue

        if search_input is None:
            raise RuntimeError("No se encontró un input visible de búsqueda en Scopus")

        search_input.click()
        search_input.press("Control+A")
        search_input.press("Backspace")
        search_input.fill(query)

        
    def search(self, query: str) -> None:
        self.fill_search_query(query)

        submit_candidates = [
            self.page.get_by_role("button", name="Search"),
            self.page.locator('button[type="submit"]').first,
        ]

        for button in submit_candidates:
            try:
                if button.count() == 0:
                    continue

                button.scroll_into_view_if_needed()
                button.wait_for(state="visible", timeout=5_000)
                button.click()
                self.wait_until_loaded()
                return
            except Exception:
                continue

        self.page.keyboard.press("Enter")
        self.wait_until_loaded()