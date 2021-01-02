#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest

import project_paths


def test_attribute_error() -> None:
    """
    It should raise an attribute error, like any normal module :/
    """
    with pytest.raises(AttributeError) as exc_info:
        project_paths.this_attribute_does_not_exist

    assert "project_paths" in str(exc_info.value)
    assert "this_attribute_does_not_exist" in str(exc_info.value)


def test_dir() -> None:
    directory = dir(project_paths)

    assert "paths" in directory
    assert directory == sorted(directory), "dir(mod) must be sorted"
