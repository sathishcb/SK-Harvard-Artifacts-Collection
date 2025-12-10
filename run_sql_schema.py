import mysql.connector

# TODO: change these to your MySQL credentials
DB_USER = "root"
DB_PASSWORD = "root"   # <---- CHANGE THIS
DB_HOST = "localhost"

SQL_FILE = "schema.sql"

def run_schema():
    # connect without database first
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # naive split by ';'
    commands = sql_script.split(";")
    for cmd in commands:
        cmd = cmd.strip()
        if cmd:
            cur.execute(cmd)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Schema executed successfully.")

if __name__ == "__main__":
    run_schema()
