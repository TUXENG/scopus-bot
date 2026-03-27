from playwright.sync_api import Page


class ScopusPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def title(self) -> str:
        return self.page.title()

    def current_url(self) -> str:
        return self.page.url

    def search_box(self):
        return self.page.locator("input").first

    def fill_search_query(self, query: str) -> None:
        search_input = self.search_box()
        search_input.wait_for()
        search_input.fill(query)

    def click_outside(self) -> None:
        self.page.locator("body").click(position={"x": 10, "y": 10})

    def click_search(self) -> None:
        search_button = self.page.get_by_role("button", name="Search", exact=True)
        search_button.wait_for()
        search_button.click()

    def search(self, query: str) -> None:
        self.fill_search_query(query)
        self.click_outside()
        self.click_search()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")