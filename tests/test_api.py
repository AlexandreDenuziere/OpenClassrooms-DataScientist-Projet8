import requests
import time

api_url = f"http://localhost:5001/api/v1/customer"

# Waiting for the API to be ready before starting tests
def wait_for_api(url, timeout=120):
    start_time = time.time()
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("API is ready!")
                return
        except requests.exceptions.ConnectionError:
            pass  # API is not ready yet
        if time.time() - start_time > timeout:
            raise TimeoutError(f"API not available after {timeout} seconds")
        time.sleep(2)  # Retry every 2 seconds

# Before lauching tests we use th e wait function
wait_for_api(api_url + "?id=100001")

def test_api_valid_customer():
    response = requests.get(f"{api_url}?id=100001")
    assert response.status_code == 200
    json_data = response.json()
    assert "Probability of the customer being a good one" in json_data
    assert "Probability of the customer being a bad one" in json_data
    assert "Result of the analysis" in json_data

def test_api_no_id():
    response = requests.get(api_url)
    assert response.status_code == 200
    assert "Error" in response.text

def test_api_invalid_id():
    response = requests.get(f"{api_url}?id=0")
    assert response.status_code == 200
    assert "Error" in response.text