import logging

from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class ResultPagination:
    NEXT_BUTTON_CANDIDATES = [
        ("role", "Next"),
        ("role", "Next page"),
        ("css", "button:has-text('Next')"),
        ("css", "span:has-text('Next') >> xpath=ancestor::button[1]"),
    ]

    CURRENT_PAGE_CANDIDATES = [
        '[aria-current="page"]',
        '[data-testid="pagination-page-current"]',
        'button[aria-current="true"]',
        'a[aria-current="page"]',
    ]

    FIRST_PAGE_CANDIDATES = [
        ("role_button", "1"),
        ("role_link", "1"),
        ("css", 'button[aria-label="Page 1"]'),
        ("css", 'a[aria-label="Page 1"]'),
        ("css", "button:has-text('1')"),
        ("css", "a:has-text('1')"),
    ]

    def __init__(self, page: Page) -> None:
        self.page = page

    def next_page_button(self) -> Locator | None:
        for selector_type, value in self.NEXT_BUTTON_CANDIDATES:
            try:
                locator = self._build_locator(selector_type, value).first
                if locator.count() > 0:
                    return locator
            except Exception:
                continue
        return None

    def has_next_page(self) -> bool:
        button = self.next_page_button()

        if button is None:
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

    def go_to_next_page(self) -> bool:
        button = self.next_page_button()

        if button is None:
            logger.warning("No se encontró botón Next")
            return False

        if not self.has_next_page():
            logger.info("El botón Next está deshabilitado o no disponible")
            return False

        try:
            button.scroll_into_view_if_needed()
            button.wait_for(state="visible", timeout=10_000)
            button.click(timeout=10_000)
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_load_state("networkidle")
            logger.info("Se avanzó a la siguiente página")
            return True
        except Exception as exc:
            logger.warning("Falló click normal en Next: %s", str(exc))

        try:
            button.scroll_into_view_if_needed()
            button.click(timeout=10_000, force=True)
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_load_state("networkidle")
            logger.info("Se avanzó a la siguiente página con force click")
            return True
        except Exception as exc:
            logger.warning("No se pudo avanzar a la siguiente página: %s", str(exc))
            return False

    def current_page_number(self) -> int | None:
        for selector in self.CURRENT_PAGE_CANDIDATES:
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

    def go_to_first_page(self) -> bool:
        current_page = self.current_page_number()

        if current_page is None:
            logger.warning("No se pudo detectar la página actual")
            return False

        if current_page == 1:
            logger.info("Ya estamos en la primera página")
            return True

        for selector_type, value in self.FIRST_PAGE_CANDIDATES:
            try:
                locator = self._build_locator(selector_type, value).first
                if locator.count() == 0:
                    continue

                locator.scroll_into_view_if_needed()
                locator.wait_for(state="visible", timeout=10_000)
                locator.click(timeout=10_000)
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_load_state("networkidle")
                logger.info("Se volvió a la primera página")
                return True
            except Exception:
                continue

        logger.warning("No se pudo volver a la primera página")
        return False

    def _build_locator(self, selector_type: str, value: str):
        if selector_type == "role":
            return self.page.get_by_role("button", name=value)
        if selector_type == "role_button":
            return self.page.get_by_role("button", name=value)
        if selector_type == "role_link":
            return self.page.get_by_role("link", name=value)
        if selector_type == "css":
            return self.page.locator(value)

        raise ValueError(f"Tipo de selector no soportado: {selector_type}")