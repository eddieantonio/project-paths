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

import inspect
import pathlib
import warnings
from os import PathLike
from pathlib import Path
from typing import Dict, Generic, List, Optional, Protocol, Tuple, TypeVar, Union, cast

import toml

# The table in pyproject.toml's [tool.*] namespace:
PYPROJECT_TABLE_NAME = "project-paths"

# the main export:
__all__ = ["paths"]
# Exceptions:
__all__ += ["ProjectPathsError", "ConfigurationNotFoundError", "PyProjectNotFoundError"]
# Advanced API:
__all__ += ["Paths", "find_caller_relative_path_to_pyproject"]


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


class Paths(Protocol):
    """
    Access paths within a parsed pyproject.toml file.
    """

    def __dir__(self) -> List[str]:
        ...

    def __getattr__(self, name: str) -> Path:
        ...

    def __len__(self) -> int:
        ...


################################### Internal classes ###################################


T = TypeVar("T")


class _ConcretePaths(Paths):
    """
    The ACTUAL implementation of Paths. Takes paths from a pyproject.toml,
    parses out the paths and enables access via attributes.
    """

    def __init__(self, path_to_pyproject_toml: PathLike):
        self._paths = _parse_pyproject_toml(Path(path_to_pyproject_toml))
        self._path_to_toml = path_to_pyproject_toml

    def __dir__(self) -> List[str]:
        return sorted(set(object.__dir__(self)) | self._paths.keys())

    def __getattr__(self, name: str) -> Path:
        try:
            return self._paths[name]
        except KeyError:
            raise AttributeError(
                f"no path named {name!r} in {self._path_to_toml}"
            ) from None

    def __len__(self) -> int:
        return len(self._paths)

    def __repr__(self) -> str:
        cls_name = type(self).__qualname__
        return f"{cls_name}({self._path_to_toml!r})"


class _Proxy(Generic[T]):
    """
    Proxy calls to regular attributes to the overriden _concrete_instance.

    Note: all __dunder__ methods (apart from __dir__) still need to be overriden in
    subclasses.
    """

    @property
    def _concrete_instance(self) -> T:
        raise NotImplementedError

    def __dir__(self) -> List[str]:
        return dir(self._concrete_instance)

    def __getattr__(self, name):
        return getattr(self._concrete_instance, name)

    def __repr__(self) -> str:
        cls_name = type(self).__qualname__
        return f"<{cls_name} routing attribute access to {self._concrete_instance!r}>"

    @classmethod
    def as_proxied_type(cls) -> T:
        """
        For type-checking purposes, returns a proxy as the type of the wrapped object.
        """
        return cast(T, cls())


class _ProjectRootProxy(_Proxy[Path]):
    """
    Acts like a pathlib.Path object but creates a concrete Path object dynamically on
    every access based on the caller's module.
    """

    @property
    def _concrete_instance(self) -> Path:
        path_to_pyproject_toml = find_caller_relative_path_to_pyproject()
        return path_to_pyproject_toml.parent

    # __dunder__ methods must be EXPLICITLY overridden:

    def __bytes__(self) -> bytes:
        return bytes(self._concrete_instance)

    # Note: will not override __eq__ and __hash__ because that may break some
    # assumptions :/

    def __fspath__(self) -> Union[str, bytes]:
        return self._concrete_instance.__fspath__()

    def __str__(self) -> str:
        return str(self._concrete_instance)

    def __truediv__(self, other) -> Path:
        return self._concrete_instance / other


class _PathsProxy(_Proxy[Paths]):
    """
    Acts like a Paths object but creates a concrete Paths object dynamically on every
    access.
    """

    @property
    def _concrete_instance(self) -> Paths:
        path_to_pyproject_toml = find_caller_relative_path_to_pyproject()
        return _ConcretePaths(path_to_pyproject_toml)

    def __len__(self) -> int:
        return len(self._concrete_instance)


##################################### External API #####################################


# The proxy intercepts attribute access and uses an appropriate concrete Paths object to
# provide the correct paths to the caller.
paths: Paths = _PathsProxy.as_proxied_type()
project_root: Path = _ProjectRootProxy.as_proxied_type()


def find_caller_relative_path_to_pyproject() -> Path:
    """
    Tries to find the pyproject.toml relative to the caller of this module.
    """

    mod_name, caller_filename = _find_caller_module_name_and_file()

    if mod_name in ("inspect", "pydoc"):
        # inspect.getmembers() might be calling us, or maybe pydoc.
        # this makes things confusing, so just use the current working dir.
        # TODO: assert that these are the built-in modules!
        return _find_pyproject_by_parent_traversal(Path.cwd())

    if isinstance(caller_filename, str):
        working_file = Path(caller_filename)
        assert working_file.is_file()
        return _find_pyproject_by_parent_traversal(working_file.parent)

    if mod_name == "__main__":
        # No filename but the mod name is __main__? Assume this is an interactive
        # prompt; thus load from the current working directory
        return _find_pyproject_by_parent_traversal(Path.cwd())

    # cannot determine filename AAAANNDD mod_name is not __main__????
    raise PyProjectNotFoundError(
        f"unable to determine filename of calling module: {mod_name}"
    )


################################## Internal functions ##################################


def _find_caller_module_name_and_file() -> Tuple[str, Optional[str]]:
    """
    Returns the module name of the first caller in the stack that DOESN'T from from this
    module -- namely, project_paths.
    """

    MODULE_EXCEPTIONS = (
        # Skip over any stack frames in THIS module
        __name__,
        # To enable Path(project_root) calls, we need to ignore
        # stack frames from pathlib
        pathlib.__name__,
    )

    try:
        # Crawl up the stack until we no longer find a caller in THIS module or any
        # excluded module (e.g., ignore calls within pathlib)
        for frame_info in inspect.stack():
            mod_name = frame_info.frame.f_globals.get("__name__")
            if mod_name not in MODULE_EXCEPTIONS:
                assert isinstance(mod_name, str)
                filename = frame_info.frame.f_globals.get("__file__")
                return mod_name, filename
        raise RuntimeError(f"cannot find any caller outside of {__name__}")
    finally:
        # Remove a reference cycle caused due to holding frame_info.frame
        # See: https://docs.python.org/3/library/inspect.html#the-interpreter-stack
        del frame_info


def _find_pyproject_by_parent_traversal(base: Path) -> Path:
    """
    Returns the path to pyproject.toml relative to the given base path.
    Traverses BACKWARDS starting from the base and going out of the parents.
    """
    for directory in [base, *base.resolve().parents]:
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate

    raise PyProjectNotFoundError(
        f"cannot find pyproject.toml within {base} or any of its parents"
    )


def _make_path(base: Path, segment: str) -> Path:
    """
    Returns the segment relative to the given base, if it's a relative path
    Absolute paths are returned as is.
    """
    original_path = Path(segment)
    if original_path.is_absolute():
        return original_path

    return base.joinpath(original_path)


def _parse_pyproject_toml(pyproject_path: Path) -> Dict[str, Path]:
    """
    Given a pyproject.toml, parses its texts and returns a dictionary of valid paths.
    """
    with pyproject_path.open() as toml_file:
        pyproject = toml.load(toml_file)

    try:
        config = pyproject["tool"][PYPROJECT_TABLE_NAME]
    except KeyError:
        raise ConfigurationNotFoundError(
            f"cannot find [tool.{PYPROJECT_TABLE_NAME}]"
            f" within {pyproject_path.resolve()}"
        )

    base = pyproject_path.parent
    assert base.is_dir()

    paths = {}
    for name, path_str in config.items():
        if name.startswith("_"):
            # discard reserved name
            warnings.warn(
                UserWarning(f"{name} is inaccessible due to leading underscore")
            )
            continue

        paths[name] = _make_path(base, path_str)

    return paths
