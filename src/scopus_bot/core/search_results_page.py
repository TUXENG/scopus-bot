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

    # -----------------------------
    # Preparación de resultados
    # -----------------------------
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

    # -----------------------------
    # Subject area facet
    # -----------------------------
    def subject_area_group(self) -> Locator:
        return self.page.locator('[data-testid="facet-group-subject-area"]')

    def open_subject_area_modal(self) -> None:
        group = self.subject_area_group()
        group.wait_for()

        show_all_button = group.get_by_role("button", name="Show all")
        show_all_button.wait_for()
        show_all_button.click()

        self.subject_area_modal().wait_for()

    def subject_area_modal(self) -> Locator:
        return self.page.locator('section[role="document"]').filter(
            has=self.page.locator('[data-testid^="facet-option-"]')
        ).first

    def click_limit_to(self) -> None:
        modal = self.subject_area_modal()
        button = modal.get_by_role("button", name="Limit to", exact=True)
        button.wait_for()
        button.click()
        self.wait_until_loaded()

    def apply_subject_area_limit(
        self,
        mapping: dict[str, str],
    ) -> dict[str, list[str]]:
        self.open_subject_area_modal()

        modal = self.subject_area_modal()

        selected: list[str] = []
        missing: list[str] = []

        for name, test_id in mapping.items():
            locator = modal.locator(f'[data-testid="{test_id}"]')

            if locator.count() == 0:
                missing.append(name)
                continue

            locator.first.click()
            selected.append(name)

        if not selected:
            raise RuntimeError(
                "No se pudo seleccionar ninguna subject area dentro del modal"
            )

        self.click_limit_to()

        return {
            "selected": selected,
            "missing": missing,
        }