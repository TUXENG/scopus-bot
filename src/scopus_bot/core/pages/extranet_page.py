from playwright.sync_api import Page


class ExtranetPage:
    LIBRARY_RESOURCES_BUTTON = "text=Bases de Datos y Libros Electrónicos"

    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.locator(self.LIBRARY_RESOURCES_BUTTON).wait_for(state="visible")

    def open_library_resources_in_new_tab(self) -> Page:
        button = self.page.locator(self.LIBRARY_RESOURCES_BUTTON)

        with self.page.context.expect_page() as new_page_info:
            button.click()

        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        return new_page