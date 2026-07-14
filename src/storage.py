import sqlite3

DB_PATH = "data/economic_data.db"


def init_db():
    """Create the observations and series_metadata tables if they don't already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            series_id TEXT NOT NULL,
            date TEXT NOT NULL,
            value REAL,
            PRIMARY KEY (series_id, date)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS series_metadata (
            series_id TEXT PRIMARY KEY,
            title TEXT,
            frequency TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_observations(series_id: str, observations: list):
    """Insert or update observation rows for a given series."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for obs in observations:
        cursor.execute("""
            INSERT OR REPLACE INTO observations (series_id, date, value)
            VALUES (?, ?, ?)
        """, (series_id, obs["date"], obs["value"]))
    conn.commit()
    conn.close()


def save_series_metadata(series_id: str, title: str, frequency: str):
    """Insert or update the human-readable title and frequency for a series."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO series_metadata (series_id, title, frequency)
        VALUES (?, ?, ?)
    """, (series_id, title, frequency))
    conn.commit()
    conn.close()