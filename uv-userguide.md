# 10 commonly used commands.
## uv init [project-name]
Initialize a new Python project with a directory, pyproject.toml, lockfile, and starter files.

## uv add [package] / uv add -r requirements.txt
Add a dependency to the project; updates pyproject.toml and the lockfile automatically.

## uv remove [package]
Remove a dependency from the project and update the environment and lockfile.

## uv sync
Sync your environment to exactly match the lockfile (creates or updates .venv).

## uv run [script.py]
Run a Python script in your project environment; ensures dependencies are installed as needed.

## uv pip install [package]
Install packages in the current environment, compatible with pip syntax.

## uv pip uninstall [package]
Uninstall packages from the environment.

## uv pip freeze
List installed packages, like pip freeze.

## uv venv [env_name]
Create a new virtual environment manually (optional, as uv projects auto-manage .venv).

## uv python [COMMAND]

=============================

# Tool Management
##uv tool run [TOOL]
Runs a tool provided by a Python package in an ephemeral (temporary) isolated environment, similar to pipx or uvx. You can specify versions with syntax like ruff@0.5.0.

## uv tool install [PACKAGE]
Installs a CLI tool globally in an isolated environment so it’s always available.

## uv tool upgrade [TOOL]
Upgrades an installed tool, respecting original version constraints.

## uv tool list
Lists all tools installed via uv.

## uv tool uninstall [TOOL]
Removes a globally installed tool.

## uv tool update-shell
Ensures the uv tool executables directory is in your system PATH, so installed tools are accessible from your shell.

# Package Management
## uv pip compile [requirements.in]
Compiles a requirements input file into a full requirements.txt or pylock.toml, resolving dependencies.

## uv pip list
Lists all packages installed in the current environment, in tabular format.

## uv pip show [PACKAGE]
Displays information about installed packages.

## uv pip tree
Shows the dependency tree for the current Python environment.

## uv pip check
Checks that all installed packages have compatible dependencies.

# Environment Management
## uv lock
Regenerates the lockfile (uv.lock) for your project to capture dependencies’ exact versions.

## uv build
Builds your Python package into a source (sdist) and/or binary (wheel) distribution.

## uv publish
Uploads built packages to PyPI or other package indexes.

## uv venv
Creates a new virtual environment manually (if needed).

## uv cache clean/prune/dir
Cleans, prunes, or inspects uv’s cache to save disk space or troubleshoot environment issues.