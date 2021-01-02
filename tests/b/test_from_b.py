#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pathlib import Path

from project_paths import paths


def test_from_b():
    """
    Same test as test_from_a, but making sure that a DIFFERENT pyproject.toml gets loaded
    """

    assert paths.filename.resolve().samefile(Path(__file__))
