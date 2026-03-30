from playwright.sync_api import Page


class ResultViewControls:
    SORT_SELECT = "select:has(option[value='cp-f'])"
    DISPLAY_SELECT = (
        "select:has(option[label='200 results']), "
        "select:has(option:text('200 results'))"
    )

    def __init__(self, page: Page) -> None:
        self.page = page

    def set_sort_by_cited_highest(self) -> None:
        sort_select = self.page.locator(self.SORT_SELECT)
        sort_select.wait_for(state="visible", timeout=10_000)
        sort_select.select_option(value="cp-f")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def set_display_200_results(self) -> None:
        display_select = self.page.locator(self.DISPLAY_SELECT).first
        display_select.wait_for(state="visible", timeout=10_000)
        display_select.select_option(label="200 results")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def prepare_results_view(self) -> None:
        self.set_sort_by_cited_highest()
        self.set_display_200_results()