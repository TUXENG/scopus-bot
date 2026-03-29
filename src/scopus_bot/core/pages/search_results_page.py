from playwright.sync_api import Locator, Page
import logging

logger = logging.getLogger(__name__)

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
    
    def next_page_button(self) -> Locator:
        candidates = [
            self.page.get_by_role("button", name="Next"),
            self.page.get_by_role("button", name="Next page"),
            self.page.locator("button", has_text="Next").first,
            self.page.locator("span:has-text('Next')").locator("xpath=ancestor::button[1]").first,
        ]

        for locator in candidates:
            try:
                if locator.count() > 0:
                    return locator
            except Exception:
                continue

        return self.page.locator("__never_matches__")


    def has_next_page(self) -> bool:
        self.scroll_to_bottom()
        button = self.next_page_button()

        if button.count() == 0:
            return False

        try:
            aria_disabled = button.get_attribute("aria-disabled")
            disabled_attr = button.get_attribute("disabled")

            if aria_disabled == "true":
                return False

            if disabled_attr is not None:
                return False

            return True
        except Exception:
            return False

    def scroll_to_top(self) -> None:
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
            self.page.wait_for_timeout(500)

            # segundo scroll por si hay lazy UI
            self.page.evaluate("window.scrollTo(0, 0)")
            self.page.wait_for_timeout(500)

        except Exception:
            pass
    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)

    def go_to_next_page(self) -> bool:
        self.scroll_to_bottom()

        button = self.next_page_button()

        if button.count() == 0:
            logger.warning("No se encontró botón Next")
            return False

        if not self.has_next_page():
            logger.info("El botón Next está deshabilitado o no disponible")
            return False

        try:
            logger.info("Haciendo scroll hacia el botón Next")
            button.scroll_into_view_if_needed()
            button.wait_for(state="visible", timeout=10_000)

            logger.info("Intentando click en Next")
            button.click(timeout=10_000)

            self.wait_until_loaded()
            logger.info("Se avanzó a la siguiente página")
            return True
        except Exception as exc:
            logger.warning("Falló click normal en Next: %s", str(exc))

        try:
            logger.info("Intentando click forzado en Next")
            button.scroll_into_view_if_needed()
            button.click(timeout=10_000, force=True)

            self.wait_until_loaded()
            logger.info("Se avanzó a la siguiente página con force click")
            return True
        except Exception as exc:
            logger.warning("No se pudo avanzar a la siguiente página: %s", str(exc))
            return False

    def current_page_number(self) -> int | None:
        selectors = [
            '[aria-current="page"]',
            '[data-testid="pagination-page-current"]',
            'button[aria-current="true"]',
            'a[aria-current="page"]',
        ]

        for selector in selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.count() == 0:
                    continue

                text = locator.inner_text().strip()
                digits = "".join(ch for ch in text if ch.isdigit())

                if digits:
                    return int(digits)
            except Exception:
                continue

        return None
    
    #Regresar a la primera pagina.
    def go_to_first_page(self) -> bool:
        current_page = self.current_page_number()

        if current_page is None:
            logger.warning("No se pudo detectar la página actual")
            return False

        if current_page == 1:
            logger.info("Ya estamos en la primera página")
            return True

        candidates = [
            self.page.get_by_role("button", name="1"),
            self.page.get_by_role("link", name="1"),
            self.page.locator('button[aria-label="Page 1"]').first,
            self.page.locator('a[aria-label="Page 1"]').first,
            self.page.locator("text=1").first,
        ]

        for locator in candidates:
            try:
                if locator.count() == 0:
                    continue

                locator.scroll_into_view_if_needed()
                locator.wait_for(state="visible", timeout=10_000)
                locator.click(timeout=10_000)
                self.wait_until_loaded()
                logger.info("Se volvió a la primera página")
                return True
            except Exception:
                continue

        logger.warning("No se pudo volver a la primera página")
        return False
    def set_year_to(self, year: int) -> None:
        try:
            # ⚠️ bajar porque el filtro suele estar abajo
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1000)

            input_to = self.page.locator('[data-testid="input-range-to"]').first

            if input_to.count() == 0:
                raise RuntimeError("No se encontró el input 'to' del filtro de año")

            input_to.scroll_into_view_if_needed()
            input_to.wait_for(state="visible", timeout=10_000)

            input_to.click()
            input_to.press("Control+A")
            input_to.press("Backspace")
            input_to.fill(str(year))

            # ⚠️ algunos filtros requieren Enter
            input_to.press("Enter")

            self.wait_until_loaded()

        except Exception as exc:
            raise RuntimeError(f"No se pudo establecer el filtro de año TO: {year}") from exc