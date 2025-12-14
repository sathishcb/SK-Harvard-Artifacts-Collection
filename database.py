import pandas as pd
from sqlalchemy import create_engine, text


# ---------------------------------------------------
# CREATE DATABASE IF NOT EXISTS
# ---------------------------------------------------
def create_database_if_missing(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    """
    Creates database only if it does not exist.
    Works on MySQL and TiDB (if privileges exist).
    """

    root_engine = create_engine(
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/",
        pool_pre_ping=True
    )

    try:
        with root_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            conn.commit()
            print(f"Database '{DB_NAME}' verified/created successfully.")
    except Exception as e:
        print(f"[INFO] Database creation skipped or insufficient privileges: {e}")


# ---------------------------------------------------
# CREATE ENGINE FOR SPECIFIC DATABASE
# ---------------------------------------------------
def get_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    return create_engine(
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        pool_pre_ping=True
    )


# ---------------------------------------------------
# RUN SCHEMA.SQL TO CREATE TABLES
# ---------------------------------------------------
def run_schema(engine, schema_file="schema.sql"):
    with open(schema_file, "r") as f:
        sql_script = f.read()

    statements = [s.strip() for s in sql_script.split(";") if s.strip()]

    with engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()

    print("Schema executed successfully!")


# ---------------------------------------------------
# INSERT ARTIFACT DATA (NO LOGIC CHANGED)
# ---------------------------------------------------
def insert_artifact_data(engine, st):
    df1 = pd.DataFrame(st.session_state.data["meta"])
    df2 = pd.DataFrame(st.session_state.data["media"])
    df3 = pd.DataFrame(st.session_state.data["colors"])

    with engine.connect() as conn:
        existing = pd.read_sql("SELECT id FROM artifact_metadata", conn)
    existing_ids = set(existing["id"])

    df1 = df1[~df1["id"].isin(existing_ids)]
    df2 = df2[df2["objectid"].isin(df1["id"])]
    df3 = df3[df3["objectid"].isin(df1["id"])]

    if df1.empty:
        st.warning("⚠ No new records to insert (duplicate prevention).")
        return False

    df1.to_sql("artifact_metadata", engine, if_exists="append", index=False)
    df2.to_sql("artifact_media", engine, if_exists="append", index=False)
    df3.to_sql("artifact_colors", engine, if_exists="append", index=False)

    st.success("✔ Data Inserted Successfully!")

    with engine.connect() as conn:
        st.header("📌 Metadata")
        st.dataframe(pd.read_sql("SELECT * FROM artifact_metadata ORDER BY id", conn),
                     use_container_width=True)

        st.header("📌 Media")
        st.dataframe(pd.read_sql("SELECT * FROM artifact_media ORDER BY objectid", conn),
                     use_container_width=True)

        st.header("📌 Colors")
        st.dataframe(pd.read_sql("SELECT * FROM artifact_colors ORDER BY objectid", conn),
                     use_container_width=True)

    return True
