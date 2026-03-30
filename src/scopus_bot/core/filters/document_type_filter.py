import logging

from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class DocumentTypeFilter:
    FACET_GROUP = '[data-testid="facet-group-document-type"]'
    MODAL_TITLE = "Filter by document type"
    SHOW_ALL_BUTTON = "Show all"
    LIMIT_TO_BUTTON = "Limit to"

    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.group().wait_for(state="visible", timeout=10_000)

    def group(self) -> Locator:
        return self.page.locator(self.FACET_GROUP)

    def modal(self) -> Locator:
        return self.page.locator('section[role="document"]').filter(
            has=self.page.get_by_text(self.MODAL_TITLE, exact=True)
        ).first

    def clear(self) -> bool:
        group = self.group()
        group.wait_for(state="visible", timeout=10_000)

        clear_button = group.get_by_text("Clear", exact=False)

        if clear_button.count() == 0:
            logger.info("No había filtro de document type para limpiar")
            return False

        clear_button.first.click()
        self.wait_until_loaded()
        logger.info("Filtro de document type limpiado")
        return True

    def open_modal(self) -> None:
        group = self.group()
        group.wait_for(state="visible", timeout=10_000)

        show_all_button = group.get_by_role("button", name=self.SHOW_ALL_BUTTON)

        if show_all_button.count() == 0:
            raise RuntimeError("No se encontró el botón 'Show all' en document type")

        show_all_button.click()
        self.modal().wait_for(state="visible", timeout=10_000)

    def apply(self, test_id: str) -> None:
        self.open_modal()
        modal = self.modal()

        option = modal.locator(f'[data-testid="{test_id}"]').first
        option.wait_for(state="visible", timeout=10_000)
        option.click()

        limit_to = modal.get_by_role("button", name=self.LIMIT_TO_BUTTON, exact=True)
        limit_to.wait_for(state="visible", timeout=10_000)
        limit_to.click()

        self.wait_until_loaded()

    def reset_and_apply(self, test_id: str) -> None:
        self.clear()
        self.apply(test_id)

    def validate_applied(self, expected_name: str) -> bool:
        group = self.group()

        try:
            group.wait_for(state="visible", timeout=10_000)
            applied_text = group.inner_text(timeout=10_000)

            if expected_name in applied_text:
                logger.info("Validación document type aplicada correctamente: %s", expected_name)
                return True

            logger.warning(
                "No se pudo validar en el grupo el document type aplicado: %s",
                expected_name,
            )
            return False
        except Exception as exc:
            logger.warning(
                "Error validando document type '%s': %s",
                expected_name,
                str(exc),
            )
            return False