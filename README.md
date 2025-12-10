# 🎨🏛 Harvard Artifacts Collection — ETL, SQL Analytics & Streamlit Dashboard  
### End-to-End Data Engineering Project using Harvard Art Museums API

## 📘 Table of Contents
- Overview
- Features
- Architecture
- Tech Stack
- Database Schema
- Project Structure
- Setup Instructions
- Running the Application
- App Workflow
- SQL Queries (25 Included)
- Screenshots
- Author

# 📌 Overview
This project is a complete **ETL + SQL Analytics + Streamlit Dashboard** solution built using the **Harvard Art Museums API**.  
It enables users to fetch **2500 artifacts per classification**, clean & normalize data, store it into MySQL/TiDB, and run **25 analytical SQL queries** inside an interactive dashboard.

# 🚀 Features
- Fast async API ingestion (up to 2500 records)
- ETL pipeline for Metadata, Media, and Color data
- Responsive Streamlit UI
- MySQL / TiDB Cloud database support
- 25 powerful SQL queries for analytics
- Duplicate-safe SQL insertion
- Live data previews

# 🏗 Architecture
Harvard API → Async ETL → Cleaning → SQL DB → Streamlit UI → Query Engine

# 🧰 Tech Stack
- **Python**, **aiohttp**, **asyncio**, **Streamlit**
- **MySQL / TiDB Cloud**
- **SQLAlchemy**, **Pandas**
- **Harvard Art Museums API**

# 🗄 Database Schema
## 1. artifact_metadata
Stores general information about artifacts.
- id (Primary Key)
- title  
- culture  
- period  
- century  
- medium  
- dimensions  
- description  
- department  
- classification  
- accessionyear  
- accessionmethod  

## 2. artifact_media
- objectid (FK → metadata.id)
- imagecount  
- mediacount  
- colorcount  
- rank  
- datebegin  
- dateend  

## 3. artifact_colors
- objectid (FK → metadata.id)
- color  
- spectrum  
- hue  
- percent  
- css3  

# 📁 Project Structure
Harvard-Artifacts-Project/  
│── app.py  
│── README.md  
│── requirements.txt  
│── database/schema.sql  

# ⚙️ Setup Instructions
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

# ▶️ Running the Application
```bash
streamlit run app.py
```

# 🧭 App Workflow
1. Select classification  
2. Collect 2500 records  
3. View 3-section data preview  
4. Migrate to SQL  
5. Insert into 3 tables  
6. Run SQL queries  
7. View results  

# 🧮 SQL Queries (25 Included)
Queries include:  
- Metadata filters  
- Media analysis  
- Color analytics  
- Multi-table joins  
- Classification insights  
- Ranking-based results  

# 👨‍💻 Author
**Sathish Kumar**  
Data Engineering | ETL | SQL | API Integrations  

If this helped, ⭐ star the repo!

