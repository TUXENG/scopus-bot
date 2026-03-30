from playwright.sync_api import Page


class PortalLoginPage:
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    SUBMIT_BUTTON = "button:has-text('Ingresar')"

    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_loaded(self) -> None:
        self.page.wait_for_selector(self.USERNAME_INPUT, state="visible")

    def fill_username(self, username: str) -> None:
        self.page.locator(self.USERNAME_INPUT).fill(username)

    def fill_password(self, password: str) -> None:
        self.page.locator(self.PASSWORD_INPUT).fill(password)

    def click_ingresar(self) -> None:
        self.page.locator(self.SUBMIT_BUTTON).click()

    def wait_until_authenticated(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def login(self, username: str, password: str) -> None:
        self.wait_until_loaded()
        self.fill_username(username)
        self.fill_password(password)
        self.click_ingresar()
        self.wait_until_authenticated()