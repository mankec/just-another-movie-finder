from enum import Enum


class SkipExternalTests(Enum):
    YES = True
    NO = False

    @property
    def reason(self):
        return "Send requests to external URLs only when testing locally. Never in CI."
