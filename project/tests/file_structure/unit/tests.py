import os
import glob
from pathlib import Path

from django.test import TestCase

from core.test.mixins import CustomAssertionsMixin

class MetaUnitTestCase(TestCase, CustomAssertionsMixin):
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
        for item in fd.iterdir():
            if item.is_dir() and (fd := item):
                if not self._init_file(fd):
                    self._raise_invalid_python_module_error(fd)
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
