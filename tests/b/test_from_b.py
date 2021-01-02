#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Same test as test_from_a, but making sure that a DIFFERENT pyproject.toml gets loaded
"""

from pathlib import Path


def test_from_a():
    from project_paths import paths

    assert paths.filename.resolve().samefile(Path(__file__))
