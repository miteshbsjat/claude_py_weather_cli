# Beautiful Weather CLI 🌤️

A beautiful, terminal-based weather application built with Python. This CLI leverages the Open-Meteo API to fetch real-time weather data, presenting the results in a clean, highly-formatted manner using the `rich` library.

## ✨ Features

*   **Simple CLI Interface:** Built with `typer`, making it easy to use from the command line.
*   **API Integration:** Automatically resolves city names to coordinates using Open-Meteo's geocoding service before fetching weather data.
*   **Beautiful Output:** Utilizes `rich` for stunning, styled terminal output, including structured tables for metrics.
*   **Robust Error Handling:** Gracefully manages network failures and city-not-found errors, displaying user-friendly messages instead of raw stack traces.

## 🚀 Getting Started

### Prerequisites

You need Python installed (3.8+) and the `uv` package manager.

### Installation

1.  **Clone the repository** (if applicable).
2.  **Install dependencies:** Since we use `uv` for management, run:

    ```bash
    uv sync
    ```

### Usage

To get the current weather for a city, simply run the application followed by the city name.

```bash
uv run main.py [CITY_NAME]
```

**Example:**

```bash
uv run main.py London
```

## 🔧 Technical Overview

### Architecture Flow

The application follows a two-step API flow to ensure accuracy:

1.  **Geocoding:** The input `[CITY_NAME]` is sent to the Open-Meteo Geocoding API (`/v1/search`) to retrieve precise latitude and longitude coordinates.
2.  **Weather Fetching:** The coordinates are then used to query the main Open-Meteo Weather API (`/v1/forecast`), retrieving current weather metrics (Temperature, Humidity, Weather Code).

### Technologies Used

*   **Python:** Core language.
*   **Typer:** Used as the command-line interface framework.
*   **httpx:** The asynchronous HTTP client used for making API requests.
*   **Rich:** Provides beautiful console formatting and structured tables for terminal output.
*   **uv:** Package and script runner manager.

## 🐞 Error Handling

The CLI is designed to be resilient:

*   **City Not Found:** If the geocoding service cannot find a match for the given city, a clear error message is displayed to the user.
*   **Network Failure:** If connectivity issues occur during either the geocoding or weather fetching process, the corresponding `httpx.HTTPError` is caught, and a formatted network error message is shown via `rich` without crashing the application.

---
*🤖 Built with Claude Code*
