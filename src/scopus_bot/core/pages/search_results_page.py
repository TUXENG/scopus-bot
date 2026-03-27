from playwright.sync_api import Locator, Page


class SearchResultsPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def current_url(self) -> str:
        return self.page.url

    def title(self) -> str:
        return self.page.title()

    def set_sort_by_cited_highest(self) -> None:
        sort_select = self.page.locator("select:has(option[value='cp-f'])")
        sort_select.wait_for()
        sort_select.select_option(value="cp-f")
        self.wait_until_loaded()

    def set_display_200_results(self) -> None:
        display_select = self.page.locator(
            "select:has(option[label='200 results']), "
            "select:has(option:text('200 results'))"
        ).first
        display_select.wait_for()
        display_select.select_option(label="200 results")
        self.wait_until_loaded()

    def prepare_results_view(self) -> None:
        self.set_sort_by_cited_highest()
        self.set_display_200_results()