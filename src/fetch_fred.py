import os
import requests
from dotenv import load_dotenv

from storage import init_db, save_observations

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
        "LRUNTTTTAUM156S",
        "QAUR628BIS",
        "IRLTLT01AUM156N",
        "NGDPRSAXDCAUQ",
        "AUSSPASTT01GYM",
        "NBAUBIS",
        "TRESEGAUM052N",
        "LRINTTMAAUM156N",
        "LRACTTMAAUQ156S",
    ]

    print("Validating series IDs...\n")
    valid_ids = [sid for sid in series_ids if validate_series(sid)]

    print("\nInitialising database...")
    init_db()

    print("\nFetching and saving observations...")
    for sid in valid_ids:
        data = get_observations(sid)
        save_observations(sid, data)
        print(f"Saved {len(data)} observations for {sid}")