from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_selector("input[name='username']")

    def fill_username(self, username: str) -> None:
        self.page.fill("input[name='username']", username)

    def fill_password(self, password: str) -> None:
        self.page.fill("input[name='password']", password)

    def click_ingresar(self) -> None:
        self.page.click("button:has-text('Ingresar')")

    def login(self, username: str, password: str) -> None:
        self.wait_until_loaded()
        self.fill_username(username)
        self.fill_password(password)
        self.click_ingresar()
        self.page.wait_for_load_state("domcontentloaded")