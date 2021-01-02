#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pathlib import Path

import pytest


def test_find_pyproject_toml():
    """
    Automatically find a pyproject.toml within the current current working directory.
    """

    from project_paths import find_caller_relative_path_to_pyproject

    # .parent == tests/, .parent.parent == repo root
    expected_pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    # We want to find the pyproject.toml for THIS project.
    pyproject_path = find_caller_relative_path_to_pyproject()
    assert pyproject_path.samefile(expected_pyproject_path)
    assert isinstance(pyproject_path, Path)
    assert pyproject_path.is_file()

    # THIS project is called "project-paths", so we should probably find that.
    pyproject_text = pyproject_path.read_text(encoding="UTF-8")
    assert "project-paths" in pyproject_text


def test_auto_discovery():
    # import within the test to prevent any magic happening when pytest imports this
    # file.
    from project_paths import find_caller_relative_path_to_pyproject, paths

    assert len(paths) >= 1
    assert hasattr(paths, "tests")
    assert "tests" in dir(paths)
    assert isinstance(paths.tests, Path)

    with pytest.raises(AttributeError) as exc_info:
        paths.does_not_exist

    assert "does_not_exist" in str(exc_info.value)
    path_str = str(find_caller_relative_path_to_pyproject())
    assert path_str in str(exc_info.value)
