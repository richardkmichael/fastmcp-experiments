# Project setup

- The `pyproject.toml` file contains information about the project, build system, testing tools, etc.
- Dependencies are added, removed and managed with the `uv` command; run `uv help` to learn more
- Run `uv sync` if dependencies need to be installed

# FastMCP dependency

- This project might use a local and modified FastMCP library, this is helpful in development when working on FastMCP itself and using this project to test FastMCP changes
- Use `uv pip show fastmcp` or read `pyproject.toml` to determine this, and the path to the modified FastMCP
- If so, ensure the editable FastMCP directory is available, and ask the human operator for access if not
- The local FastMCP directory is also a git repository, so be sure use git as necessary
  - e.g., With your Bash tool, directly: `git -C ../fastmcp [command]`, or `pushd ../fastmcp ; git [command] ; popd`

# Testing

- If tests are written, use `pytest`
- Store the Pytest configuration in `pyproject.toml`

# Code formatting

- Code is linted and formatted using `ruff`; run `uv run ruff help` to learn more
- Run `uv run ruff check .` and `uv run ruff format .` to ensure code follows project standards
