#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Access paths from pyproject.toml

-----
Usage
-----

Add the following table to your pyproject.toml:

.. code-block:: toml

    [tool.project-paths]
    # You can place as many paths as you want:
    tests = "path/to/my/tests/"
    docs = "path/to/my/docs/"
    other = "path/to/literally/anything-else.txt"
    absolute = "/opt/absolute/path"

Then access it in your Python application:

.. code-block:: python

    from project_paths import paths

    # Elements are pathlib.Path objects:
    paths.tests.is_dir()
    paths.docs / "README.md"
    paths.other.write_text("hello")
    assert paths.absolute.exists()

"""

import os
from pathlib import Path
from typing import Dict, List

import toml

# How to access the automatic paths object.
PATHS_ATTRIBUTE_NAME = "paths"
# The table in pyproject.toml's [tool.*] namespace:
PYPROJECT_TABLE_NAME = "project-paths"

# the main export:
__all__ = [PATHS_ATTRIBUTE_NAME]
# exceptions:
__all__ = ["ProjectPathsError", "ConfigurationNotFoundError", "PyProjectNotFoundError"]
# advanced API:
__all__ = ["Paths", "find_path_to_pyproject"]


###################################### Exceptions ######################################


class ProjectPathsError(Exception):
    """
    Base class for all errors thrown from this module
    """


class ConfigurationNotFoundError(ProjectPathsError):
    f"""
    Raised when the [tool.{PYPROJECT_TABLE_NAME}] table cannot be found in the
    pyproject.toml file.
    """


class PyProjectNotFoundError(ProjectPathsError):
    """
    Raised when an appropriate pyproject.toml cannot be found.
    """


####################################### Classes ########################################


class Paths:
    """
    Access paths within a parsed pyproject.toml file.
    """

    def __init__(self, configuration_path: Path):
        self._paths = self._parse_paths(configuration_path)
        # TODO: warn if any keys have a leading underscore

    def _parse_paths(self, pyproject_path: Path) -> Dict[str, Path]:
        with pyproject_path.open() as toml_file:
            pyproject = toml.load(toml_file)

        try:
            config = pyproject["tool"][PYPROJECT_TABLE_NAME]
        except KeyError:
            raise ConfigurationNotFoundError(
                f"cannot find [tool.{PYPROJECT_TABLE_NAME}]"
                f" within {pyproject_path.resolve()}"
            )

        return {key: Path(path_str) for key, path_str in config.items()}

    def __getattr__(self, name: str) -> Path:
        try:
            return self._paths[name]
        except KeyError:
            raise AttributeError from None

    def __dir__(self) -> List[str]:
        return sorted(set(super().__dir__()) | self._paths.keys())

    def __len__(self) -> int:
        return len(self._paths)


############################### Functions: External API ################################


def find_path_to_pyproject() -> Path:
    """
    Tries to find the pyproject.toml relative to the current working directory.
    """
    # TODO: make this relative to the **caller's** module.
    cwd = Path(os.getcwd())
    for directory in (cwd,) + tuple(cwd.parents):
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate

    raise PyProjectNotFoundError(
        f"cannot find pyproject.toml within {cwd} or its parents"
    )


######################################## Magic #########################################

# This is a dynamically-loaded Paths object.
# it's instantiation is handled by __getattr__()
paths: Paths


def __getattr__(name: str) -> Paths:
    """
    Enables lazy-loading of the .path attribute.

    [PEP-562]: https://www.python.org/dev/peps/pep-0562/
    """
    if name == PATHS_ATTRIBUTE_NAME:
        return _get_default_paths()
    raise AttributeError


# TODO: implement __dir__?


def _get_default_paths() -> Paths:
    global paths

    if PATHS_ATTRIBUTE_NAME not in globals():
        pyproject_path = find_path_to_pyproject()
        paths = Paths(pyproject_path)

    return paths
