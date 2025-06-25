from pathlib import Path

from django.test import TestCase, tag

from core.tests.mixins import CustomAssertionsMixin
from core.tests.utils import ChromeMode
from project import settings


@tag("sanity_check")
class SanityCheckUnitTestCase(TestCase, CustomAssertionsMixin):
    def _raise_invalid_python_module_error(self, fd):
        raise ValueError(
            f"'{fd}' is not a proper Python module."
        )

    def _init_file(self, fd):
        return next(
            (
                f for f in fd.iterdir()
                if f.name == "__init__.py"
            ),
            None
        )

    def _subdirs(self, fd):
        return [x for x in fd.iterdir() if x.is_dir()]

    def _inspect_fd(self, fd):
        if not self._init_file(fd):
            self._raise_invalid_python_module_error(fd)
        for item in fd.iterdir():
            if item.is_dir():
                fd = item
                self._inspect_fd(fd)

    def test_each_tests_folder_and_its_descendants_must_be_proper_python_modules(self):
        subdirs = self._subdirs(Path.cwd())
        apps_and_project = [
            fd for fd in subdirs
            if "apps.py" in (f.name for f in fd.iterdir()) or fd.name == "project"
        ]
        for fd in apps_and_project:
            if not self._init_file(fd):
                self._raise_invalid_python_module_error(fd)
            tests_dir = next(
                (
                    fd for fd in fd.iterdir()
                    if fd.is_dir() and fd.name == "tests"
                ),
                None
            )
            if not tests_dir:
                continue
            if not self._subdirs(tests_dir):
                continue
            self._inspect_fd(tests_dir)

    def test_optional_settings_must_be_properly_set(self):
        self.assertTrue(
            settings.SKIP_EXTERNAL_TESTS.value,
            settings.SKIP_EXTERNAL_TESTS.reason
        )
        self.assertEqual(
            settings.CHROME_OPTIONS.arguments,
            ChromeMode.HEADLESS.options.arguments,
            ChromeMode.HEADLESS.reason
        )
