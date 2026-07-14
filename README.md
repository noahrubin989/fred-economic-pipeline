# Australia Macro Data Pipeline

A data pipeline that pulls Australian macroeconomic indicators from the [FRED API](https://fred.stlouisfed.org/docs/api/fred/), stores them in SQLite, and surfaces them through an interactive Streamlit dashboard.

Covers: API ingestion, data validation, persistent storage, and reporting on streamlit

**Live demo:** [fred-economic-pipeline.streamlit.app](https://fred-economic-pipeline.streamlit.app/)

## What it does

```
FRED API → validation → SQLite storage → Streamlit dashboard
```

1. **Ingest** — pulls historical observations for a set of Australian macro series from FRED
2. **Validate** — confirms each series ID actually resolves before fetching data, so a broken/renamed ID fails loudly and early rather than silently
3. **Store** — writes observations and series metadata (human-readable titles, frequency) into a local SQLite database, using idempotent upserts so re-running the pipeline is always safe
4. **Explore** — an interactive dashboard to select series, filter by date range, view trends, and export data to CSV

## Series covered

| Series ID | Description | Frequency |
|---|---|---|
| `LRUNTTTTAUM156S` | Unemployment rate (15+) | Monthly |
| `LRINTTMAAUM156N` | Inactivity rate, male (15+) | Monthly |
| `LRACTTMAAUQ156S` | Labor force participation rate, male (15+) | Quarterly |
| `IRLTLT01AUM156N` | 10-year government bond yield | Monthly |
| `QAUR628BIS` | Real residential property prices | Quarterly |
| `NGDPRSAXDCAUQ` | Real GDP | Quarterly |
| `AUSSPASTT01GYM` | Share prices (All Ordinaries) | Monthly |
| `NBAUBIS` | Broad effective exchange rate | Monthly |
| `TRESEGAUM052N` | Total reserves excluding gold | Monthly |

All series are sourced from FRED (originally published by the OECD, BIS, or IMF depending on series). Series titles and frequencies are pulled directly from FRED's own metadata at ingestion time, rather than hardcoded, so adding a new series never requires touching the dashboard code.

## Setup

**1. Clone the repo and install dependencies**

```bash
git clone git@github.com:noahrubin989/fred-economic-pipeline.git
cd fred-economic-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Get a free FRED API key**

Register at [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org) and request an API key.

**3. Set up your environment file**

```bash
cp .env.example .env
```

Then edit `.env` and add your key:

```
FRED_API_KEY=your_key_here
```

**4. Run the ingestion pipeline**

```bash
python src/fetch_fred.py
```

This validates each series, initializes the database, and pulls full available history for all nine series into `data/economic_data.db`.

**5. Launch the dashboard**

```bash
streamlit run app.py
```

## Project structure

```
fred-economic-pipeline/
├── app.py                    # Streamlit dashboard
├── src/
│   ├── fetch_fred.py         # FRED API ingestion + validation
│   └── storage.py            # SQLite schema + read/write logic
├── notebooks/
│   └── notebook.ipynb        # Exploratory analysis
├── data/
│   └── economic_data.db      # Committed to the repo (see note below) so the hosted app has data to serve
├── requirements.txt
├── .env.example
└── README.md
```

## Design notes

A few decisions worth calling out, since they weren't arbitrary:

- **SQLite over CSV** — allows proper typing, idempotent upserts via a composite primary key (`series_id`, `date`), and real SQL queries rather than re-parsing flat files.
- **Values stored as `REAL`, not `TEXT`** — FRED occasionally returns `"."` for missing observations; this is converted to `NULL` at ingestion time so every downstream consumer (notebook, dashboard) gets clean, correctly-typed data without repeating the same cleanup logic.
- **Series titles stored in the database, not hardcoded in the app** — the dashboard reads human-readable labels from a `series_metadata` table populated directly from FRED's own metadata. Adding a new series to the ingestion list is the only step needed for it to show up correctly labeled everywhere.
- **Raw index-level comparisons can be misleading** — some macro series (e.g. CPI across countries) use different base years, so comparing raw levels rather than growth rates can produce a misleading picture. Worth keeping in mind when extending this analysis.
- **Scope** — this project intentionally stays focused on Australia rather than expanding indefinitely across countries or indicators. A small, well-understood set of series is more useful than a large, shallow one.
- **The SQLite database is committed to the repo, against the usual "don't commit generated data" rule** — this is a deliberate exception made for deployment. Streamlit Community Cloud clones the repo fresh on each deploy, and since `data/*.db` was gitignored, the hosted app had no database to read from and failed on startup. Force-adding the `.db` file (`git add -f`) gives the hosted app something to serve without requiring the FRED API key to be re-run as a cloud secret. For a larger or frequently-changing dataset, the better long-term fix would be running the ingestion script on app startup (or on a schedule) rather than committing the database itself.

## Future work

Deliberately out of scope for now, but natural next steps:

- Scheduled refresh via GitHub Actions (e.g. weekly pull of latest observations)
- A more formal bronze/silver/gold layering as the pipeline grows
- Expanding series coverage (e.g. commodity prices, credit aggregates) if a specific analytical question calls for it
- Basic automated tests around series validation and the storage layer

## Tech stack

Python · SQLite · pandas · Streamlit · Plotly · FRED API
