import logging

from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class SubjectAreaFilter:
    FACET_GROUP = '[data-testid="facet-group-subject-area"]'
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
            has=self.page.locator('[data-testid^="facet-option-"]')
        ).first

    def clear(self) -> bool:
        group = self.group()
        group.wait_for(state="visible", timeout=10_000)

        clear_button = group.get_by_text("Clear", exact=False)

        if clear_button.count() == 0:
            logger.info("No había subject areas para limpiar")
            return False

        clear_button.first.click()
        self.wait_until_loaded()
        logger.info("Filtro de subject area limpiado")
        return True

    def open_modal(self) -> None:
        group = self.group()
        group.wait_for(state="visible", timeout=10_000)

        show_all_button = group.get_by_role("button", name=self.SHOW_ALL_BUTTON)

        if show_all_button.count() == 0:
            raise RuntimeError("No se encontró el botón 'Show all' en subject area")

        show_all_button.click()
        self.modal().wait_for(state="visible", timeout=10_000)

    def apply_limit(self, mapping: dict[str, str]) -> dict[str, list[str]]:
        self.open_modal()
        modal = self.modal()

        selected: list[str] = []
        missing: list[str] = []

        for name, test_id in mapping.items():
            option = modal.locator(f'[data-testid="{test_id}"]').first

            if option.count() == 0:
                missing.append(name)
                continue

            option.click()
            selected.append(name)

        if not selected:
            raise RuntimeError("No se pudo seleccionar ninguna subject area")

        limit_to = modal.get_by_role("button", name=self.LIMIT_TO_BUTTON, exact=True)
        limit_to.wait_for(state="visible", timeout=10_000)
        limit_to.click()

        self.wait_until_loaded()

        return {
            "selected": selected,
            "missing": missing,
        }

    def validate_applied(self, expected_names: list[str]) -> bool:
        group = self.group()

        try:
            group.wait_for(state="visible", timeout=10_000)
            applied_text = group.inner_text(timeout=10_000)

            matched = [name for name in expected_names if name in applied_text]

            if matched:
                logger.info(
                    "Validación subject area aplicada correctamente: %s",
                    ", ".join(matched),
                )
                return True

            logger.warning(
                "No se pudo validar en el grupo ninguna subject area aplicada: %s",
                ", ".join(expected_names),
            )
            return False
        except Exception as exc:
            logger.warning(
                "Error validando subject areas '%s': %s",
                ", ".join(expected_names),
                str(exc),
            )
            return False