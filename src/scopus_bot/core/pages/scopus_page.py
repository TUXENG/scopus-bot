from playwright.sync_api import Locator, Page


class ScopusPage:
    SIGN_IN_BUTTON = '[data-testid="header-sign-in"]'
    INSTITUTION_LOGIN_BUTTON = "#bdd-elsSecondaryBtn"

    SEARCH_INPUT_CANDIDATES = [
        "#autosuggest-k1bsp1a1jer-input",
        'input[id^="autosuggest-"][id$="-input"]',
        'input[role="combobox"]',
        'input[type="search"]:visible',
        'input[aria-label*="search" i]:visible',
    ]

    SEARCH_BUTTON_CANDIDATES = [
        'button[type="submit"]',
    ]

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_selector(self.SIGN_IN_BUTTON, state="visible")

    def click_sign_in(self) -> None:
        self.page.locator(self.SIGN_IN_BUTTON).click()

    def click_institution_login(self) -> None:
        self.page.wait_for_selector(self.INSTITUTION_LOGIN_BUTTON, state="visible")
        self.page.locator(self.INSTITUTION_LOGIN_BUTTON).click()

    def wait_until_ready_for_search(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")
        self._find_search_input(timeout=10_000)

    def current_url(self) -> str:
        return self.page.url

    def title(self) -> str:
        return self.page.title()

    def fill_search_query(self, query: str) -> None:
        search_input = self._find_search_input(timeout=10_000)
        search_input.scroll_into_view_if_needed()
        search_input.click()
        search_input.press("Control+A")
        search_input.press("Backspace")
        search_input.fill(query)

    def search(self, query: str) -> None:
        self.fill_search_query(query)

        if self._click_search_button():
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_load_state("networkidle")
            return

        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def _find_search_input(self, timeout: int = 5_000) -> Locator:
        for selector in self.SEARCH_INPUT_CANDIDATES:
            try:
                locator = self.page.locator(selector).first
                locator.wait_for(state="visible", timeout=timeout)
                return locator
            except Exception:
                continue

        raise RuntimeError("No se encontró un input visible de búsqueda en Scopus")

    def _click_search_button(self) -> bool:
        for selector in self.SEARCH_BUTTON_CANDIDATES:
            try:
                button = self.page.locator(selector).first
                button.wait_for(state="visible", timeout=5_000)
                button.scroll_into_view_if_needed()
                button.click()
                return True
            except Exception:
                continue

        return False