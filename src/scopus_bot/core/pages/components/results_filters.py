from playwright.sync_api import Page


class ResultsFilters:
    YEAR_TO_INPUT = '[data-testid="input-range-to"]'

    def __init__(self, page: Page) -> None:
        self.page = page

    def set_year_to(self, year: int) -> None:
        input_to = self.page.locator(self.YEAR_TO_INPUT).first

        if input_to.count() == 0:
            raise RuntimeError("No se encontró el input 'to' del filtro de año")

        input_to.scroll_into_view_if_needed()
        input_to.wait_for(state="visible", timeout=10_000)

        input_to.click()
        input_to.press("Control+A")
        input_to.press("Backspace")
        input_to.fill(str(year))
        input_to.press("Enter")

        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")