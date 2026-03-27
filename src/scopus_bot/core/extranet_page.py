from playwright.sync_api import Page


class ExtranetPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.locator("text=Bases de Datos y Libros Electrónicos").wait_for()

    def open_library_resources(self) -> None:      
        locator = self.page.locator("text=Bases de Datos y Libros Electrónicos")
        locator.wait_for()
        locator.click()