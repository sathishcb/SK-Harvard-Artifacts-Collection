import asyncio
import pandas as pd
import streamlit as st

# Local modules
from config import API_KEY, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from api import fetch_harvard
from database import get_engine,insert_artifact_data,create_database_if_missing, get_engine, run_schema
from queries import SQL_QUERIES
from sqlalchemy import text


# ------------------------------------------------------------------
# DATABASE ENGINE
# ------------------------------------------------------------------


# Create DB if missing
create_database_if_missing(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

# Create engine for selected DB
engine = get_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

# Run schema.sql (tables)
run_schema(engine)


# ------------------------------------------------------------------
# STREAMLIT PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(page_title="Harvard Artifacts", layout="wide")
st.markdown("<h1 style='text-align:center;'>🎨 🏛 Harvard’s Artifacts Collection</h1>",
            unsafe_allow_html=True)


# ------------------------------------------------------------------
# UI - CLASSIFICATION INPUT
# ------------------------------------------------------------------
classification = st.selectbox(
    "Select Classification",
    [
        "Coins", "Paintings", "Sculpture", "Drawings",
        "Jewelry", "Textile Arts", "Furniture", "Manuscripts"
    ]
)

btn_collect = st.button("Collect Data", use_container_width=True)

st.markdown("<h3 style='text-align:center;'>🔽 Select Your Choice</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
btn_migrate = col1.button("Migrate to SQL", use_container_width=True)
btn_queries = col2.button("SQL Queries", use_container_width=True)

st.markdown("---")


# ------------------------------------------------------------------
# SESSION STATE INIT
# ------------------------------------------------------------------
defaults = {
    "data": {"meta": [], "media": [], "colors": []},
    "show_insert": False,
    "insert_disabled": False,
    "show_queries": False,
}

for key, val in defaults.items():
    st.session_state.setdefault(key, val)

if "last_class" not in st.session_state:
    st.session_state.last_class = classification


# Reset when classification changes
if classification != st.session_state.last_class:
    st.session_state.show_insert = False
    st.session_state.insert_disabled = False
    st.session_state.show_queries = False
    st.session_state.data = {"meta": [], "media": [], "colors": []}
    st.session_state.last_class = classification


# ------------------------------------------------------------------
# COLLECT DATA BUTTON
# ------------------------------------------------------------------
if btn_collect:
    with st.spinner("⚡ Fetching 2500 Records..."):
        meta, media, colors = asyncio.run(fetch_harvard(API_KEY, classification))

    st.session_state.data = {"meta": meta, "media": media, "colors": colors}
    st.session_state.show_insert = False
    st.session_state.show_queries = False
    st.session_state.insert_disabled = False

    st.success(f"✔ {classification} — 2500 Records Collected")

    c1, c2, c3 = st.columns(3)
    c1.subheader("📌 Metadata")
    c1.json(meta[:1])
    c2.subheader("🖼 Media")
    c2.json(media[:1])
    c3.subheader("🎨 Color")
    c3.json(colors[:5])


# ------------------------------------------------------------------
# SQL QUERIES SECTION
# ------------------------------------------------------------------
if btn_queries:
    st.session_state.show_queries = True
    st.session_state.show_insert = False

if st.session_state.show_queries:
    st.header("🔍 SQL Queries")

    query_list = ["Select a Query"] + list(SQL_QUERIES.keys())
    selected_query = st.selectbox("Choose a SQL Query", query_list)

    params = {}
    if selected_query.startswith("16."):  # Only query requiring parameters
        params["id"] = st.text_input("Enter Artifact ID")

    if st.button("Run Query"):
        if selected_query == "Select a Query":
            st.warning("Please select a query.")
        else:
            try:
                with engine.connect() as conn:
                    df = pd.read_sql(text(SQL_QUERIES[selected_query]), conn, params=params)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Error: {e}")

    st.stop()  # Prevent insert panel from appearing simultaneously


# ------------------------------------------------------------------
# INSERT SECTION
# ------------------------------------------------------------------
# ---------------- INSERT UI SECTION ----------------
if btn_migrate:
    if not st.session_state.data["meta"]:
        st.warning("⚠ Please collect data before migrating to SQL.")
        st.session_state.show_insert = False
        st.session_state.show_queries = False
    else:
        st.session_state.show_insert = True
        st.session_state.show_queries = False

if st.session_state.show_insert and not st.session_state.show_queries:
    st.subheader("Insert the Collected Data into Database")

    if st.session_state.insert_disabled:
        if st.session_state.data["meta"]:
            st.info("✔ Data already inserted — collect a new classification to enable insert.")

    else:
        if st.button("Insert", disabled=st.session_state.insert_disabled):
            result = insert_artifact_data(engine, st)

            if result:
                st.session_state.insert_disabled = True
