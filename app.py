import asyncio
import aiohttp
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# ---------------- API & DB CONFIG ----------------
API_KEY = "--------" # <---- CHANGE THIS
#engine = create_engine("mysql+mysqlconnector://root:root@localhost:3306/harvard_artifacts", pool_pre_ping=True)
#TiDB Cloud:
#engine = create_engine("mysql+mysqlconnector://<user>:<password>@<host>:4000/<database>")
DB_USER = "root"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_NAME = "harvard_artifacts"
DB_PORT = 3306   # MySQL = 3306, TiDB = 4000

ENGINE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(ENGINE_URL, pool_pre_ping=True)

# ---------------- FAST ASYNC FETCH 2500 ----------------
async def fetch_page(session, url, params):
    async with session.get(url, params=params) as resp:
        return await resp.json()

async def fetch_harvard(classification):
    base = "https://api.harvardartmuseums.org/object"
    tasks = []
    async with aiohttp.ClientSession() as session:
        for page in range(1, 40):
            params = {"apikey": API_KEY, "classification": classification, "size": 100, "page": page}
            tasks.append(fetch_page(session, base, params))
        results = await asyncio.gather(*tasks)

    metadata, media, colors = [], [], []

    for res in results:
        for r in res.get("records", []):
            oid = r.get("id")
            if not oid:
                continue

            metadata.append({
                "id": oid, "title": r.get("title"), "culture": r.get("culture"),
                "period": r.get("period"), "century": r.get("century"), "medium": r.get("medium"),
                "dimensions": r.get("dimensions"), "description": r.get("description"),
                "department": r.get("department"), "classification": r.get("classification"),
                "accessionyear": r.get("accessionyear"), "accessionmethod": r.get("accessionmethod")
            })
            media.append({
                "objectid": oid, "imagecount": r.get("imagecount"), "mediacount": r.get("mediacount"),
                "colorcount": r.get("colorcount"), "rank": r.get("rank"),
                "datebegin": r.get("datebegin"), "dateend": r.get("dateend")
            })
            for c in r.get("colors") or []:
                colors.append({
                    "objectid": oid, "color": c.get("color"), "spectrum": c.get("spectrum"),
                    "hue": c.get("hue"), "percent": c.get("percent"), "css3": c.get("css3")
                })

    return metadata[:2500], media[:2500], colors

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Harvard Artifacts", layout="wide")
st.markdown("<h1 style='text-align:center;'>🎨 🏛 Harvard’s Artifacts Collection</h1>", unsafe_allow_html=True)

classification = st.selectbox("Select Classification", [
    "Coins", "Paintings", "Sculpture", "Drawings",
    "Jewelry", "Textile Arts", "Furniture", "Manuscripts"
])

btn_collect = st.button("Collect Data", use_container_width=True)
st.markdown("<h3 style='text-align:center;'>🔽 Select Your Choice</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
btn_migrate = col1.button("Migrate to SQL", use_container_width=True)
btn_queries = col2.button("SQL Queries", use_container_width=True)
st.markdown("---")

# ---------------- SESSION STATE ----------------
for key, default in {
    "data": {"meta": [], "media": [], "colors": []},
    "show_insert": False,
    "insert_disabled": False,
    "show_queries": False
}.items():
    st.session_state.setdefault(key, default)

 # Reset insert panel if user changes classification
if "last_class" not in st.session_state:
    st.session_state.last_class = classification

if classification != st.session_state.last_class:
    st.session_state.show_insert = False
    st.session_state.insert_disabled = False
    st.session_state.show_queries = False
    st.session_state.data = {"meta": [], "media": [], "colors": []}
    st.session_state.last_class = classification
   

# ---------------- COLLECT ----------------
if btn_collect:
    with st.spinner("⚡ Fetching 2500 Records..."):
        meta, media, colors = asyncio.run(fetch_harvard(classification))

    st.session_state.data = {"meta": meta, "media": media, "colors": colors}
    st.session_state.show_insert = False
    st.session_state.show_queries = False
    st.session_state.insert_disabled = False

    st.success(f"✔ {classification} — 2500 Records Collected")

    c1, c2, c3 = st.columns(3)
    c1.subheader("📌 Metadata Preview"); c1.json(meta[:1])
    c2.subheader("🖼 Media Preview"); c2.json(media[:1])
    c3.subheader("🎨 Color Preview"); c3.json(colors[:5])

# ---------------- SQL QUERIES MUST RUN FIRST ----------------
if btn_queries:
    st.session_state.show_queries = True
    st.session_state.show_insert = False

if st.session_state.show_queries:
    st.header("🔍 SQL Queries")

    queries = {

    # ---------- artifact_metadata ----------
    "1. 11th century Byzantine artifacts":
        "SELECT * FROM artifact_metadata WHERE century='11th century' AND culture='Byzantine'",

    "2. Unique cultures represented":
        "SELECT DISTINCT culture FROM artifact_metadata WHERE culture IS NOT NULL",

    "3. Artifacts from Archaic Period":
        "SELECT * FROM artifact_metadata WHERE period='Archaic'",

    "4. Titles ordered by accession year (DESC)":
        "SELECT title, accessionyear FROM artifact_metadata ORDER BY accessionyear DESC",

    "5. Artifacts count per department":
        "SELECT department, COUNT(*) AS total FROM artifact_metadata GROUP BY department",

    "6. Oldest 20 artifacts (by accession year)":
        "SELECT * FROM artifact_metadata ORDER BY accessionyear ASC LIMIT 20",


    # ---------- artifact_media ----------
    "7. Artifacts with more than 1 image":
        """
        SELECT am.title, m.imagecount 
        FROM artifact_media m
        JOIN artifact_metadata am ON am.id = m.objectid
        WHERE m.imagecount > 1
        """,

    "8. Average rank of all artifacts":
        "SELECT AVG(`rank`) AS avg_rank FROM artifact_media",

    "9. Artifacts where colorcount > mediacount":
        """
        SELECT am.title, m.colorcount, m.mediacount
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        WHERE m.colorcount > m.mediacount
        """,

    "10. Artifacts created between 1500 and 1600":
        """
        SELECT am.title, m.datebegin, m.dateend 
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        WHERE m.datebegin >= 1500 AND m.dateend <= 1600
        """,

    "11. Artifacts with no media files":
        "SELECT COUNT(*) AS no_media FROM artifact_media WHERE mediacount = 0 OR mediacount IS NULL",

    "12. Maximum imagecount per classification":
        """
        SELECT am.classification, MAX(m.imagecount) AS max_images
        FROM artifact_media m
        JOIN artifact_metadata am ON am.id = m.objectid
        GROUP BY am.classification
        """,


    # ---------- artifact_colors ----------
    "13. All distinct hues used":
        "SELECT DISTINCT hue FROM artifact_colors WHERE hue IS NOT NULL",

    "14. Top 5 most used colors":
        """
        SELECT color, COUNT(*) AS frequency
        FROM artifact_colors
        GROUP BY color
        ORDER BY frequency DESC
        LIMIT 5
        """,

    "15. Average coverage percent for each hue":
        """
        SELECT hue, AVG(percent) AS avg_percent
        FROM artifact_colors
        GROUP BY hue
        """,

    "16. Colors used for a given artifact ID":
        "SELECT * FROM artifact_colors WHERE objectid = :id",

    "17. Total number of color entries":
        "SELECT COUNT(*) AS total_colors FROM artifact_colors",

    "18. Hue frequency per classification":
        """
        SELECT am.classification, c.hue, COUNT(*) AS hue_count
        FROM artifact_colors c
        JOIN artifact_metadata am ON am.id = c.objectid
        GROUP BY am.classification, c.hue
        """,


    # ---------- JOIN Queries ----------
    "19. Artifact titles + hues (Byzantine culture)":
        """
        SELECT am.title, c.hue
        FROM artifact_metadata am
        JOIN artifact_colors c ON am.id = c.objectid
        WHERE am.culture = 'Byzantine'
        """,

    "20. Each artifact title with all hues":
        """
        SELECT am.title, c.hue
        FROM artifact_metadata am
        JOIN artifact_colors c ON am.id = c.objectid
        ORDER BY am.title
        """,

    "21. Titles, cultures, and ranks (period NOT NULL)":
        """
        SELECT am.title, am.culture, m.`rank`
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        WHERE am.period IS NOT NULL
        """,

    "22. Top 10 ranked artifacts that include hue 'Grey'":
        """
        SELECT DISTINCT am.title, m.`rank`
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        JOIN artifact_colors c ON am.id = c.objectid
        WHERE c.hue = 'Grey'
        ORDER BY m.`rank`
        LIMIT 10
        """,

    "23. Artifacts per classification + average media count":
        """
        SELECT am.classification, COUNT(*) AS total_artifacts,
               AVG(m.mediacount) AS avg_media
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        GROUP BY am.classification
        """,

    "24. Count artifacts grouped by century":
        """
        SELECT century, COUNT(*) AS total
        FROM artifact_metadata
        GROUP BY century
        ORDER BY century
        """,

    "25. Most common hue used per classification":
        """
        SELECT am.classification, c.hue, COUNT(*) AS hue_count
        FROM artifact_colors c
        JOIN artifact_metadata am ON am.id = c.objectid
        GROUP BY am.classification, c.hue
        ORDER BY hue_count DESC
        """
}


   # UI → dropdown list
    query_list = ["Select a Query"] + list(queries.keys())
    selected_query = st.selectbox("Choose a SQL Query", query_list)


    # Parameter input for Query #14
    params = {}
    if selected_query.startswith("14."):
        params["id"] = st.text_input("Enter Artifact ID")

    if st.button("Run Query"):
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text(queries[selected_query]), conn, params=params)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Error: {e}")

    st.stop()   # Important → prevents insert section from showing

# ---------------- INSERT ----------------
# ---------------- MIGRATE BUTTON LOGIC ----------------
if btn_migrate:
    # If no data collected → show alert
    if not st.session_state.data["meta"]:
        st.warning("⚠ Please collect data before migrating to SQL.")
        st.session_state.show_insert = False
        st.session_state.show_queries = False
    else:
        # Allow insert panel
        st.session_state.show_insert = True
        st.session_state.show_queries = False

if st.session_state.show_insert and not st.session_state.show_queries:
    st.subheader("Insert the Collected Data into Database")

    if st.session_state.insert_disabled and not st.session_state.show_queries:

        if st.session_state.data["meta"]:   # Only show if old data still exists
            st.info("✔ Data already inserted — collect a new classification to enable insert.")

    else:
        if st.button("Insert", disabled=st.session_state.insert_disabled):
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
            else:
                df1.to_sql("artifact_metadata", engine, if_exists="append", index=False)
                df2.to_sql("artifact_media", engine, if_exists="append", index=False)
                df3.to_sql("artifact_colors", engine, if_exists="append", index=False)
                st.success("✔ Data Inserted Successfully!")

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
                    

            st.session_state.insert_disabled = True



