from playwright.sync_api import Locator, Page
import logging

logger = logging.getLogger(__name__)

class SubjectAreaFilter:
    def __init__(self, page: Page) -> None:
        self.page = page

    #Validaciones
    def validate_applied(self, expected_names: list[str]) -> bool:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

        body_text = self.page.locator("body").inner_text(timeout=10_000)

        for name in expected_names:
            if name in body_text:
                logger.info("Validación subject area encontrada en página: %s", name)
                return True

        logger.warning(
            "No se pudo validar visualmente ninguna subject area aplicada: %s",
            ", ".join(expected_names),
        )
        return False

    #Carga
    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    #subject area
    def group(self) -> Locator:
        return self.page.locator('[data-testid="facet-group-subject-area"]')

    #Abrir el modal
    def open_modal(self) -> None:
        group = self.group()
        group.wait_for()

        show_all_button = group.get_by_role("button", name="Show all")
        show_all_button.wait_for()
        show_all_button.click()

        self.modal().wait_for()

    # Cargar el modal
    def modal(self) -> Locator:
        return self.page.locator('section[role="document"]').filter(
            has=self.page.locator('[data-testid^="facet-option-"]')
        ).first

    # Marcar checkbox
    def apply_limit(self, mapping: dict[str, str]) -> dict[str, list[str]]:
        self.open_modal()
        modal = self.modal()

        selected: list[str] = []
        missing: list[str] = []

        for name, test_id in mapping.items():
            option = modal.locator(f'[data-testid="{test_id}"]')

            if option.count() == 0:
                missing.append(name)
                continue

            option.first.click()
            selected.append(name)

        if not selected:
            raise RuntimeError(
                "No se pudo seleccionar ninguna subject area"
            )

        limit_to = modal.get_by_role("button", name="Limit to", exact=True)
        limit_to.wait_for()
        limit_to.click()

        self.wait_until_loaded()

        return {
            "selected": selected,
            "missing": missing,
        }