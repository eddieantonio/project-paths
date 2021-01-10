project-paths
=============

[![Lint and Test](https://github.com/eddieantonio/project-paths/workflows/Lint%20and%20Test/badge.svg)](https://github.com/eddieantonio/project-paths/actions?query=workflow%3A%22Lint+and+Test%22)
[![codecov](https://codecov.io/gh/eddieantonio/project-paths/branch/main/graph/badge.svg?token=1L6746DIHY)](https://codecov.io/gh/eddieantonio/project-paths)
[![PyPI](https://img.shields.io/pypi/v/project-paths)](https://pypi.org/project/project-paths/)

Access file paths from `pyproject.toml`

> Thanks to [@Madoshakalaka](https://github.com/madoshakalaka) for the idea!

```toml
# pyproject.toml
[tool.project-paths]
readme = "README.md"
```

```python
# app.py
from project_paths import paths

# paths.readme is a pathlib.Path object:
print(paths.readme.read_text())
```

Install
-------

    pip install project-paths


Usage
-----

Does your application have a bunch of configurable file paths? Do you
wish you just had one place to configure list them all?

### Add paths to `[tool.project-paths]`

With this module, define your paths in your `pyproject.toml` file under
the `[tool.project-paths]` table:

```toml
[tool.project-paths]
docs = "path/to/my/docs"
settings = "path/to/my/settings.py"
config = "/opt/path/to/my/config
# Add as many paths as you want!
```

Anything string defined with `[tool.project-paths]` will be made
available. Relative paths are relative to `pyproject.toml`.

### Access paths using `project_paths.paths.<path name>`

Now you can access all the paths listed in `pyproject.toml` with
`project_paths.paths`. Every path is returned as
a [`pathlib.Path`][pathlib] object:

```python
from project_paths import paths

print(paths.docs.glob("*.md"))
assert paths.config.exists()
exec(paths.settings.read_text())
# Or anything you want!
```

### Access your project root directory using `project_root`

You can access the project root directory (assumed to be the directory
that contains `pyproject.toml`) using `project_root`, which acts like
a `pathlib.Path` object:

```python
from project_paths import project_root

assert project_root.is_dir()
assert (project_root / "pyproject.toml").is_file()
print((project_root / "README.md").read_text())
```

> **Note**: `project_root` is not a true `Path` object. Use
> `Path(project_root)` to obtain a true `Path` object.


### Caveats

Names in `[tool.project-paths]` should be a valid Python identifier
and the names **cannot** have a leading underscore. If a name has
a leading underscore, a warning is issued and the name is inaccessible:

```toml
[tool.project-paths]
# BAD: paths that start with a '_' cannot be used
_my_path = "path/to/wherever"
# GOOD: path is a valid Python identifier!
my_path = "path/to/wherever"
```

[pathlib]: https://docs.python.org/3/library/pathlib.html
[tool-table]: https://www.python.org/dev/peps/pep-0518/#tool-table


### Errors

All intentional errors inherit from `project_paths.ProjectPathError`.

#### `PyProjectNotFoundError`

Raised when `project_paths` cannot find an appropriate `pyproject.toml`
for the caller. This can happen if the caller simply does not have
a `pyproject.toml` file, or when it's not possible to determine the
caller's filename.

> **NOTE**: if accessing paths from the interactive console,
> `project_paths` will find the appropriate `pyproject.toml` relative to
> the current working directory!


#### `ConfigurationNotFoundError`

Raised when `project_paths` cannot find the `[tool.project-paths]` table
within the `pyproject.toml` file. Perhaps there is a typo or perhaps the
`project_paths` inferred the incorrect module path.


License
-------

2021 © Eddie Antonio Santos. MIT Licensed.
