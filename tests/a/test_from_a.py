#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests that this module gets its configuration from its pyproject.toml file.
"""

from pathlib import Path


def test_from_a():
    from project_paths import paths

    assert paths.filename.resolve().samefile(Path(__file__))
