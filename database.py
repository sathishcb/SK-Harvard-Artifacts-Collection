import pandas as pd
from sqlalchemy import create_engine

def get_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    url = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(url, pool_pre_ping=True)

def insert_artifact_data(engine, st):


    df1 = pd.DataFrame(st.session_state.data["meta"])
    df2 = pd.DataFrame(st.session_state.data["media"])
    df3 = pd.DataFrame(st.session_state.data["colors"])

    # Load existing IDs
    with engine.connect() as conn:
        existing = pd.read_sql("SELECT id FROM artifact_metadata", conn)
    existing_ids = set(existing["id"])

    # Duplicate filtering (same logic)
    df1 = df1[~df1["id"].isin(existing_ids)]
    df2 = df2[df2["objectid"].isin(df1["id"])]
    df3 = df3[df3["objectid"].isin(df1["id"])]

    # No new rows
    if df1.empty:
        st.warning("⚠ No new records to insert (duplicate prevention).")
        return False

    # Insert records (same logic)
    df1.to_sql("artifact_metadata", engine, if_exists="append", index=False)
    df2.to_sql("artifact_media", engine, if_exists="append", index=False)
    df3.to_sql("artifact_colors", engine, if_exists="append", index=False)

    st.success("✔ Data Inserted Successfully!")

    # Display tables (same UI output)
    with engine.connect() as conn:
        st.header("📌 artifact_metadata (All Records)")
        df_meta_all = pd.read_sql("SELECT * FROM artifact_metadata ORDER BY id", conn)
        st.dataframe(df_meta_all, use_container_width=True)

        st.header("📌 artifact_media (All Records)")
        df_media_all = pd.read_sql("SELECT * FROM artifact_media ORDER BY objectid", conn)
        st.dataframe(df_media_all, use_container_width=True)

        st.header("📌 artifact_colors (All Records)")
        df_colors_all = pd.read_sql("SELECT * FROM artifact_colors ORDER BY objectid", conn)
        st.dataframe(df_colors_all, use_container_width=True)

    return True
