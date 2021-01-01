#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from pathlib import Path
from typing import Dict, List

import toml

# How to access the automatic paths object.
PATHS_ATTRIBUTE_NAME = "paths"
PYPROJECT_TABLE_NAME = "project-paths"

__all__ = ["Paths", "ProjectPathsError", "ConfigurationNotFoundError"]
__all__ += [PATHS_ATTRIBUTE_NAME]


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


class Paths:
    def __init__(self, configuration_path: Path):
        self._paths = self._parse_paths(configuration_path)

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


_paths: Paths


def _get_default_paths() -> Paths:
    global _paths

    if "_paths" not in globals():
        pyproject_path = find_path_to_pyproject()
        _paths = Paths(pyproject_path)

    return _paths


def find_path_to_pyproject() -> Path:
    """
    Tries to find the pyproject.toml relative to the current working directory.
    """
    cwd = Path(os.getcwd())
    for directory in (cwd,) + tuple(cwd.parents):
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate

    raise PyProjectNotFoundError(
        f"cannot find pyproject.toml within {cwd} or its parents"
    )


def __getattr__(name: str) -> Paths:
    if name == PATHS_ATTRIBUTE_NAME:
        return _get_default_paths()
    raise AttributeError
