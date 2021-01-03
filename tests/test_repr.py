#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Note: these tests know about the internal structure of the module.
"""

import project_paths


def test_concrete_repr():
    toml_path = project_paths.find_caller_relative_path_to_pyproject()
    paths = project_paths._ConcretePaths(toml_path)

    assert type(paths).__qualname__ in repr(paths)
    assert str(toml_path) in repr(paths)
