from playwright.sync_api import Page


class ExtranetPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.locator("text=Bases de Datos y Libros Electrónicos").wait_for()

    def open_library_resources_in_new_tab(self) -> Page:
        button = self.page.locator("text=Bases de Datos y Libros Electrónicos")

        with self.page.context.expect_page() as new_page_info:
            button.click()

        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        return new_page