from playwright.sync_api import Page

from scopus_bot.core.pages.components.result_pagination import ResultPagination
from scopus_bot.core.pages.components.result_view_controls import ResultViewControls
from scopus_bot.core.pages.components.results_filters import ResultsFilters


class SearchResultsPage:
    RESULTS_CONTAINER_CANDIDATES = [
        '[data-testid="search-results"]',
        '[data-testid="results-list"]',
        'ul[aria-label*="results" i]',
        'div:has-text("Cited by")',
    ]

    def __init__(self, page: Page) -> None:
        self.page = page
        self.pagination = ResultPagination(page)
        self.view_controls = ResultViewControls(page)
        self.filters = ResultsFilters(page)

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

        for selector in self.RESULTS_CONTAINER_CANDIDATES:
            try:
                self.page.locator(selector).first.wait_for(state="visible", timeout=10_000)
                return
            except Exception:
                continue

        self.page.wait_for_load_state("networkidle")

    def current_url(self) -> str:
        return self.page.url

    def title(self) -> str:
        return self.page.title()

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    
    #=====================================#
    #Funciones a remover en el futuro     #
    #=====================================#
    def prepare_results_view(self) -> None:
        self.view_controls.prepare_results_view()

    def set_year_to(self, year: int) -> None:
        self.filters.set_year_to(year)

    def has_next_page(self) -> bool:
        return self.pagination.has_next_page()

    def go_to_next_page(self) -> bool:
        return self.pagination.go_to_next_page()

    def go_to_first_page(self) -> bool:
        return self.pagination.go_to_first_page()