import re
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Australia Macro Explorer", layout="wide")


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "-", name)


@st.cache_data
def load_data():
    conn = sqlite3.connect("data/economic_data.db")
    df = pd.read_sql("SELECT * FROM observations", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


@st.cache_data
def load_labels():
    conn = sqlite3.connect("data/economic_data.db")
    labels = pd.read_sql("SELECT series_id, title FROM series_metadata", conn)
    conn.close()
    return dict(zip(labels["series_id"], labels["title"]))


df = load_data()
SERIES_LABELS = load_labels()

st.title("Australia Macro Data Explorer")

series_list = sorted(df["series_id"].unique())
label_to_id = {SERIES_LABELS.get(sid, sid): sid for sid in series_list}

selected_labels = st.multiselect(
    "Choose series to view",
    options=list(label_to_id.keys()),
    default=list(label_to_id.keys())[:2],
)
selected_series = [label_to_id[label] for label in selected_labels]

min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.slider(
    "Date range",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
)

filtered = df[
    (df["series_id"].isin(selected_series)) &
    (df["date"] >= date_range[0]) &
    (df["date"] <= date_range[1])
]

st.subheader("Trend")

if filtered.empty:
    st.info("No data to display — select at least one series.")
else:
    filtered_labeled = filtered.copy()
    filtered_labeled["series_name"] = filtered_labeled["series_id"].map(SERIES_LABELS)

    fig = px.line(
        filtered_labeled,
        x="date",
        y="value",
        color="series_name",
        labels={"value": "Value", "date": "Date", "series_name": "Series"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Download")

if not filtered.empty:
    for sid in selected_series:
        series_df = filtered[filtered["series_id"] == sid]
        series_name = SERIES_LABELS.get(sid, sid)
        csv = series_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=f"Download {series_name}.csv",
            data=csv,
            file_name=f"{safe_filename(series_name)}.csv",
            mime="text/csv",
            key=sid,
        )