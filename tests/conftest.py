#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
from pathlib import Path

# Required so that tests can import project_paths:
base_dir = Path(__file__).parent.parent
sys.path.insert(0, os.fspath(base_dir))
