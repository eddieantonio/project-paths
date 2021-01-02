#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest


def test_loading_problematic_names():
    """
    Names with leading underscores are reserved, and thus they are made inaccessible if
    present in the pyproject.toml file. There should be a warning in this case!
    """

    with pytest.warns(UserWarning, match="_paths"):
        from project_paths import paths
