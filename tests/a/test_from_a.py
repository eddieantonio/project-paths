#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pathlib import Path

from project_paths import paths


def test_from_a():
    """
    Tests that this module gets its configuration from its pyproject.toml file.
    See also test_from_b() which is the exact same test, but loads b instead of a.
    This exercises the following features:
     - infer correct pyproject.toml from calling module
     - base relative paths relative to pyproject.toml
    """

    assert paths.filename.resolve().samefile(Path(__file__))
