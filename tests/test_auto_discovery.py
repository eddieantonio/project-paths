#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pathlib import Path

import pytest


def test_auto_discovery():
    from project_paths import paths

    assert len(paths) >= 1
    assert hasattr(paths, "tests")
    assert "tests" in dir(paths)
    assert isinstance(paths.tests, Path)

    with pytest.raises(AttributeError):
        paths.does_not_exist
