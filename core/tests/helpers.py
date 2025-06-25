from enum import Enum


class SkipExternalTests(Enum):
    YES = True
    NO = False

    @property
    def reason(self):
        return """
        Send requests to external URLs only when testing locally. If you wish to ignore this check append `--exclude-tag=sanity_check`. Refer to https://docs.djangoproject.com/en/5.2/topics/testing/tools/#tagging-tests.
        """
