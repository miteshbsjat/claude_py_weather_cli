import pytest
from unittest.mock import patch, Mock
import httpx
import typer
from typing import Optional

# Import components from main.py
# We need to patch imports used in main.py to isolate the tests.
import main

@pytest.fixture
def mock_console():
    """Fixture to mock rich console output."""
    with patch('main.console') as mock:
        yield mock

# --- Helper Mocks ---

def mock_get_coords_success(city_name):
    """Simulates successful geocoding response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [{
            "latitude": 51.5074,
            "longitude": 0.1278
        }]
    }
    return mock_response

def mock_get_coords_failure(city_name):
    """Simulates city not found (empty results)."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    return mock_response

def mock_get_coords_network_error(*args, **kwargs):
    """Simulates a network/HTTP error during geocoding."""
    raise httpx.HTTPError("Mocked connection error")

# --- Tests for API functions ---

@patch('main.httpx.Client')
def test_get_coordinates_success(mock_client, mock_console):
    mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status.return_value = None
    mock_client.return_value.__enter__.return_value.get.return_value.json.return_value = {
        "results": [{
            "latitude": 51.5,
            "longitude": 0.1
        }]
    }

    result = main.get_coordinates_for_city("London")
    assert result == (51.5, 0.1)

@patch('main.httpx.Client')
def test_get_coordinates_city_not_found(mock_client, mock_console):
    mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status.return_value = None
    mock_client.return_value.__enter__.return_value.get.return_value.json.return_value = {"results": []}

    result = main.get_coordinates_for_city("NonExistentCity")
    assert result is None
    mock_console.print.assert_called_with("[bold red]Error:[/bold red] Could not find coordinates for 'NonExistentCity'.")

@patch('main.httpx.Client')
def test_get_coordinates_network_error(mock_client, mock_console):
    mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPError("Mocked error")

    result = main.get_coordinates_for_city("TestCity")
    assert result is None
    mock_console.print.assert_called_with("[bold red]Network Error:[/bold red] Could not connect to the geocoding service. Details: Mocked error")

@patch('main.httpx.Client')
def test_get_weather_data_success(mock_client, mock_console):
    mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status.return_value = None
    mock_client.return_value.__enter__.return_value.get.return_value.json.return_value = {
        "current": {
            "temperature_2m": 15.0,
            "relative_humidity_2m": 70,
            "weather_code": 2
        }
    }

    result = main.get_weather_data(51.5, 0.1)
    assert result is not None
    assert result['temperature_2m'] == 15.0

@patch('main.httpx.Client')
def test_get_weather_data_network_error(mock_client, mock_console):
    mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPError("Mocked error")

    result = main.get_weather_data(51.5, 0.1)
    assert result is None
    mock_console.print.assert_called_with("[bold red]Network Error:[/bold red] Could not connect to the weather service. Details: Mocked error")


# --- Integration Test for main() ---

@patch('main.display_weather')
@patch('main.get_weather_data')
@patch('main.get_coordinates_for_city')
def test_main_success_flow(mock_get_coords, mock_get_weather, mock_display, mock_console):
    # Setup mock responses for success
    mock_get_coords.return_value = (51.5, 0.1)
    mock_get_weather.return_value = {
        "temperature_2m": 15.0,
        "relative_humidity_2m": 70,
        "weather_code": 2
    }

    # Run the main function without trying to patch typer.Exit
    # It will raise typer.Exit, which pytest should handle gracefully.
    main.main("London")

    # Assertions for correct flow
    mock_get_coords.assert_called_once_with("London")
    mock_get_weather.assert_called_once_with(51.5, 0.1)
    mock_display.assert_called_once()

@patch('main.get_weather_data')
@patch('main.get_coordinates_for_city')
def test_main_geocoding_failure(mock_get_coords, mock_get_weather, mock_console):
    # Setup mock response for failure
    mock_get_coords.return_value = None

    # Use pytest.raises to assert that typer.Exit is correctly raised
    with pytest.raises(typer.Exit):
        main.main("NonExistentCity")

    # Assertions for failure
    mock_get_coords.assert_called_once_with("NonExistentCity")
    mock_get_weather.assert_not_called()


@patch('main.get_weather_data')
@patch('main.get_coordinates_for_city')
def test_main_weather_data_failure(mock_get_coords, mock_get_weather, mock_console):
    # Setup mock responses for failure
    mock_get_coords.return_value = (51.5, 0.1)
    mock_get_weather.return_value = None

    # Use pytest.raises to assert that typer.Exit is correctly raised
    with pytest.raises(typer.Exit):
        main.main("London")

    # Assertions for failure
    mock_get_coords.assert_called_once_with("London")
    mock_get_weather.assert_called_once_with(51.5, 0.1)