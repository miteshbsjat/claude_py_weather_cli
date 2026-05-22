# Beautiful Weather CLI - Developer Guide

## Project Context
This is a terminal-based weather application built with Python. It uses `typer` for the CLI interface, `httpx` for making API requests to Open-Meteo, and `rich` for formatting terminal output. 

## Build & Execution Commands
* **Run the CLI**: `uv run main.py [CITY_NAME]`
* **Add a dependency**: `uv add [PACKAGE_NAME]`
* **Sync dependencies**: `uv sync`
* **Run linting/formatting**: `uv run ruff check .` and `uv run ruff format .` (if ruff is added)

## Code Style & Architecture Guidelines
* **Tooling**: Always use `uv` for package management and script execution. Do not use `pip` or generate `requirements.txt`.
* **CLI Framework**: Use `typer` for handling arguments and commands. Avoid standard `argparse`.
* **Terminal Output**: Never use standard `print()`. Always use `rich` (specifically `rich.console.Console` and `rich.table.Table`) for terminal output to ensure beautiful formatting.
* **Typing**: Use strict Python type hints for all function arguments and return types.
* **Error Handling**: 
  * Wrap `httpx` network calls in `try/except` blocks catching `httpx.HTTPError`.
  * Display errors to the user gracefully using `rich` (e.g., red text or a styled error panel) instead of dumping raw stack traces.
* **API Usage**: Rely on the Open-Meteo API (requires no authentication). First use the geocoding endpoint to resolve the city name to coordinates, then use the weather endpoint.

## Project Structure
* Keep the core logic in `main.py` to maintain a simple, single-file architecture unless the project grows significantly.
