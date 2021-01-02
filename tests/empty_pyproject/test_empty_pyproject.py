#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pathlib import Path

import pytest

import project_paths
from project_paths import paths

HERE = Path(__file__).parent


def test_empty_pyproject_toml():
    with pytest.raises(project_paths.ConfigurationNotFoundError) as exc_info:
        len(paths)

    assert str(HERE / "pyproject.toml") in str(
        exc_info.value
    ), "error message did not specify which pyproject.toml it looked in"
