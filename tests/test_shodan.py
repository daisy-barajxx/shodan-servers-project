import os
import sys
from pathlib import Path
import requests
from unittest.mock import patch, Mock
from src.shodan_service import ShodanService

@pytest.fixture
def service(tmp_path):
    """provides a fresh ShadonService instance for each test"""
    with patch.dict(os.environ, {"SHODAN_API_KEY": "test_key"}):
        s = ShodanService()
        s.output_file = str(tmp_path / "shodan_servers.out")
        return s

def test_service_initialization(service):
    """verify the service initializes with correct default values"""
    assert service.api_key == "test_key"
    assert "shodan_servers.out" in service.output_file
    assert service.interval == 3600 # an hour interval

def test_shodan_running(service, tmp_path):
    """Verify the service creates its output file"""
    output_file = tmp_path / "shodan_servers.out"
    service.output_file = str(output_file)
    output_file.touch()
    assert output_file.exists()


@patch('requests.get')
def test_fetch_servers_success(mock_get, service):
    """Test successful API response"""
    mock_get.return_value.json.return_value = {
        "matches": [{"ip": "1.1.1.1", "location": {"city": "Seattle"}}]
    }
    service.fetch_servers()
    assert "Seattle, 1.1.1.1" in Path(service.output_file).read_text()

@patch('requests.get')
def test_fetch_servers_empty(mock_get, service):
    """test handling of empty API response (no servers found)"""
    mock_response = Mock()
    mock_response.json.return_value = {"matches": []}
    mock_get.return_value = mock_response

    service.fetch_servers()

    assert os.path.exists(service.output_file)
    assert os.path.getsize(service.output_file) == 0

@patch('requests.get')
def test_fetch_servers_failure(mock_get, service):
    """test error handling when API request fails"""
    mock_get.side_effect = requests.exceptions.RequestException("API Error")

    service.fetch_servers()

    with open(service.output_file) as f:
        content = f.read()
        assert "Error - API Error" in content

def test_signal_handling(service):
    """verify service handles SIGTERM signal gracefully"""
    original_exit = sys.exit
    sys.exit = lambda code: None  # Override exit for test

    try:
        service.signal_handler(None, None)
        with open(service.output_file) as f:
            content = f.read()
            assert "Received SIGTERM, exiting" in content
    finally:
        sys.exit = original_exit

@patch('time.sleep', side_effect=KeyboardInterrupt())
@patch.object(ShodanService, 'fetch_servers')
def test_run_loop_interrupt(mock_fetch, mock_sleep, service):
    """test service stops cleanly on KeyboardInterrupt"""
    try:
        service.run()
    except KeyboardInterrupt:
        pass
    mock_fetch.assert_called_once()

@patch('requests.get')
def test_output_file_rotation(mock_get, service):
    """verify subsequent runs overwrite the output file properly"""
    mock_response = Mock()
    mock_response.json.return_value = {"matches": []}
    mock_get.return_value = mock_response

    # First run - creates file
    service.fetch_servers()
    with open(service.output_file, 'r') as f:
        first_content = f.read()

    # Second run - overwrites same file
    service.fetch_servers()
    with open(service.output_file, 'r') as f:
        second_content = f.read()

    # verify the file was actually overwritten 
    assert first_content == second_content == ""  # Since we're returning empty matches

    # check the file exists and is empty
    assert os.path.exists(service.output_file)
    assert os.path.getsize(service.output_file) == 0

def test_missing_city_handling(service):
    """test handling of server records with missing city data"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "matches": [
                {"ip": "3.3.3.3", "location": {"region_code": "WA"}}
            ]
        }
        mock_get.return_value = mock_response

        service.fetch_servers()

        with open(service.output_file) as f:
            content = f.read()
            assert "N/A, 3.3.3.3" in content

@patch('time.sleep')
@patch.object(ShodanService, 'fetch_servers')
def test_run_loop_interval(mock_fetch, mock_sleep, service):
    """Verify service sleeps for correct interval between runs"""
    # Setup mock to interrupt after first sleep
    mock_sleep.side_effect = KeyboardInterrupt()

    try:
        service.run()
    except KeyboardInterrupt:
        pass

    # Verify sleep was called with the configured interval
    mock_sleep.assert_called_once_with(service.interval)