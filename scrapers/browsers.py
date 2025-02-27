import os
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


__all__ = ["get_browser"]


def get_browser() -> Firefox:
    """Get a headless Firefox browser

    Returns:
        Firefox: headless Firefox browser
    """
    options = Options()
    options.add_argument("--headless")

    WEBDRIVER_PATH = os.environ.get("WEBDRIVER_PATH")

    if WEBDRIVER_PATH and not os.path.exists(WEBDRIVER_PATH):
        WEBDRIVER_PATH = GeckoDriverManager().install()

    service = Service(WEBDRIVER_PATH)
    browser = Firefox(service=service, options=options)

    return browser
