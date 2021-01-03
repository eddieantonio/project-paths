#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import inspect
import os
import sys
from subprocess import check_output

import project_paths


def test_from_stdin():
    """
    Get the project path from <stdin>.
    """

    program = "from project_paths import paths; print(paths.tests)"

    env = {**os.environ}
    env.update(PYTHONPATH=":".join(sys.path))

    output = check_output([sys.executable, "-c", program], env=env, encoding="UTF-8")
    assert "/tests" in output


def test_from_pydoc_help():
    """
    Test that calling help() works; pydoc.help() likes to rummage around with
    attributes, so it's important to make sure this doesn't crash!
    """
    help(project_paths)


def test_from_inspect():
    """
    Test that inspect can finds appropriate things and does not crash!
    """

    members = dict(inspect.getmembers(project_paths.paths))
    assert "tests" in members
    assert "absolute" in members
