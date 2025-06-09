from enum import Enum

from selenium.webdriver.chrome.options import Options


class SkipExternalTests(Enum):
    YES = True
    NO = False

    @property
    def reason(self):
        return """
        Send requests to external URLs only when testing locally. If you wish to ignore this check append `--exclude-tag=ci`. Refer to https://docs.djangoproject.com/en/5.2/topics/testing/tools/#tagging-tests.
        """


class ChromeMode(Enum):
    HEADLESS = "headless"
    DEFAULT = "default"

    @property
    def options(self):
        options = Options()
        if self.value == "headless":
            options.add_argument("--headless")
        return options

    @property
    def reason(self):
        return """
        Chrome Headless mode should only be disabled when testing locally. If you wish to ignore this check append `--exclude-tag=ci`. Refer to https://docs.djangoproject.com/en/5.2/topics/testing/tools/#tagging-tests.
        """
