#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from contextlib import contextmanager
from pathlib import Path

import pytest

from project_paths import PyProjectNotFoundError, paths


@pytest.mark.skip(reason="I don't really know how to write this... :/")
def test_pyproject_not_found():
    root = Path("/")
    assert not (root / "pyproject.toml").exists()

    # TODO: the module, very reasonably, expects the filename to exist.
    # So we can't just pretend we're in the root directory if there isn't an actual file
    # there.
    # We **could** place the file in a temporary directory and hope none of the
    # descendants has a pyproject.toml...
    with set_module_filename("/test_pyproject_not_found.py"):
        with pytest.raises(PyProjectNotFoundError):
            len(paths)


@contextmanager
def set_module_filename(name):
    global __file__

    original_name = __file__
    __file__ = name
    assert globals()["__file__"] == name, "could not overwrite global"

    yield

    __file__ = original_name
