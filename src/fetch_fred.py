import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred"

def get_series_metadata(series_id: str) -> dict:
    """Fetch metadata for a FRED series (title, frequency, units, etc.)."""
    url = f"{BASE_URL}/series"
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["seriess"][0]


def get_observations(series_id: str, start: str = None, end: str = None) -> list:
    """Fetch observation data points for a FRED series."""
    url = f"{BASE_URL}/series/observations"
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
    }
    if start:
        params["observation_start"] = start
    if end:
        params["observation_end"] = end

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["observations"]


def validate_series(series_id: str) -> bool:
    """Check whether a series ID resolves on FRED before pulling data."""
    try:
        meta = get_series_metadata(series_id)
        print(f"✓ {series_id}: {meta['title']} ({meta['frequency']})")
        return True
    except requests.exceptions.HTTPError:
        print(f"✗ {series_id}: not found or invalid")
        return False


if __name__ == "__main__":
    series_ids = [
        "IR3TIB01AUM156N",  # AU 3-month interbank rate (cash rate proxy)
        "CCUSMA02AUM618N",  # AUD/USD exchange rate
        "CPALTT01AUQ657N",  # AU CPI
        "LRHUTTTTAUM156S",  # AU unemployment rate
        "FEDFUNDS",         # US Fed funds rate
        "CPIAUCSL",         # US CPI
    ]

    print("Validating series IDs...\n")
    for sid in series_ids:
        validate_series(sid)