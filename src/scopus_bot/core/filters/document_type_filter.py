from playwright.sync_api import Locator, Page


class DocumentTypeFilter:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def group(self) -> Locator:
        return self.page.locator('[data-testid="facet-group-document-type"]')

    def clear(self) -> bool:
        group = self.group()
        group.wait_for()

        clear_button = group.get_by_text("Clear", exact=False)

        if clear_button.count() == 0:
            return False

        clear_button.first.click()
        self.wait_until_loaded()
        return True

    def open_modal(self) -> None:
        group = self.group()
        group.wait_for()

        show_all_button = group.get_by_role("button", name="Show all")
        show_all_button.wait_for()
        show_all_button.click()

        self.modal().wait_for()

    def modal(self) -> Locator:
        return self.page.locator('section[role="document"]').filter(
            has=self.page.get_by_text("Filter by document type", exact=True)
        ).first

    def apply(self, test_id: str) -> None:
        self.open_modal()
        modal = self.modal()

        option = modal.locator(f'[data-testid="{test_id}"]')
        option.wait_for()
        option.first.click()

        limit_to = modal.get_by_role("button", name="Limit to", exact=True)
        limit_to.wait_for()
        limit_to.click()

        self.wait_until_loaded()

    def reset_and_apply(self, test_id: str) -> None:
        self.clear()
        self.apply(test_id)