import typer
import httpx
import rich
from rich.console import Console
from typing import Optional

# Initialize rich console for formatted output
console = Console()

# Initialize Typer application
app = typer.Typer()

# --- Constants ---
# Base URL for Open-Meteo API
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# --- API Interaction Functions ---

def get_coordinates_for_city(city_name: str) -> Optional[tuple[float, float]]:
    """
    Calls the Open-Meteo geocoding API to resolve a city name to coordinates.
    Handles network errors gracefully.
    """
    params = {
        "name": city_name,
        "count": 1,
        "language": "en"
    }

    try:
        # Use httpx.Client for persistent connections
        with httpx.Client(timeout=10.0) as client:
            response = client.get(GEOCODE_URL, params=params)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                latitude = result["latitude"]
                longitude = result["longitude"]
                return latitude, longitude
            else:
                console.print(f"[bold red]Error:[/bold red] Could not find coordinates for '{city_name}'.")
                return None
    except httpx.HTTPError as e:
        # Gracefully handle network and HTTP errors
        console.print(f"[bold red]Network Error:[/bold red] Could not connect to the geocoding service. Details: {e}")
        return None
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        return None

def get_weather_data(latitude: float, longitude: float) -> Optional[dict]:
    """
    Calls the Open-Meteo weather API to fetch weather data for given coordinates.
    Handles network errors gracefully.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,weather_code",
        "timezone": "auto"
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("current")
    except httpx.HTTPError as e:
        console.print(f"[bold red]Network Error:[/bold red] Could not connect to the weather service. Details: {e}")
        return None
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        return None

# --- Output Presentation ---

def display_weather(city_name: str, data: dict):
    """
    Displays the weather data using rich.console.Console and rich.table.Table.
    """

    # Map Open-Meteo weather codes to descriptions for better UX
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog"
    }

    weather_code = data.get("weather_code")
    description = weather_codes.get(weather_code, f"Code {weather_code} (Unknown)")

    # Use rich Table for structured and beautiful output
    console.print("\n[bold green]🌿 Beautiful Weather Report 🌿[/bold green]\n")

    table = rich.table.Table(title=f"Weather in {city_name.capitalize()}")
    table.add_column("Metric", style="cyan", justify="left")
    table.add_column("Value", style="magenta", justify="right")

    # Populate the table
    table.add_row("Temperature", f"{data.get('temperature_2m')}°C")
    table.add_row("Conditions", description)
    table.add_row("Humidity", f"{data.get('relative_humidity_2m')}%")

    console.print(table)
    console.print("\n[dim]Data provided by Open-Meteo.[/dim]")


# --- CLI Interface ---

@app.command()
def main(city_name: str):
    """
    Displays the current weather for a specified city using the Open-Meteo API.
    """
    console.print(f"[bold yellow]🔍 Looking up weather for '{city_name}'...[/bold yellow]")

    # 1. Geocoding
    coords = get_coordinates_for_city(city_name)

    if coords is None:
        # Error already displayed in get_coordinates_for_city
        raise typer.Exit(code=1)

    latitude, longitude = coords
    console.print(f"[dim]Coordinates resolved: {latitude}, {longitude}[/dim]")

    # 2. Weather Fetching
    weather_data = get_weather_data(latitude, longitude)

    if weather_data is None:
        # Error already displayed in get_weather_data
        raise typer.Exit(code=1)

    # 3. Output Presentation
    display_weather(city_name, weather_data)


if __name__ == "__main__":
    app()
