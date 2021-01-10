#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from pathlib import Path

import project_paths
import pytest
from project_paths import find_caller_relative_path_to_pyproject, paths, project_root

# These paths MUST be declared in the ACTUAL pyproject.toml for this project.
EXPECTED_PATHS = ("tests", "absolute")


def test_find_pyproject_toml():
    """
    Automatically find a pyproject.toml within the current current working directory.
    """

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


@pytest.mark.parametrize("path_name", EXPECTED_PATHS)
def test_basic_usage(path_name):
    """
    Tests basic usage of the API.
    """

    assert path_name in dir(paths)
    assert hasattr(paths, path_name)

    path = getattr(paths, path_name)
    assert isinstance(path, Path)
    assert path.is_absolute()


def test_project_root() -> None:
    # Makes this test resilient to renaming the package with an auto-refactor
    package_name = project_paths.__name__

    assert project_root.is_dir()
    assert (project_root / "pyproject.toml").is_file()
    assert (project_root / package_name).is_dir()
    assert isinstance(os.fspath(project_root), (str, bytes))


def test_len():
    assert len(paths) >= len(EXPECTED_PATHS)


def test_absolute_path():
    """
    An absolute path near the root should have few parts.
    """
    assert len(paths.absolute.parts) <= 2


def test_path_does_not_exist():
    with pytest.raises(AttributeError) as exc_info:
        paths.does_not_exist

    assert "does_not_exist" in str(exc_info.value)
    path_str = str(find_caller_relative_path_to_pyproject())
    assert path_str in str(exc_info.value)
