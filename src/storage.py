import sqlite3

DB_PATH = "data/economic_data.db"


def init_db():
    """Create the observations table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            series_id TEXT NOT NULL,
            date TEXT NOT NULL,
            value TEXT,
            PRIMARY KEY (series_id, date)
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