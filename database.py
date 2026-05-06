import sqlite3

print("🔄 Connecting to SQLite Database...")

try:
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    print("✅ SQLite Database Connected Successfully!")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT,
        role TEXT
    )
    """)
    db.commit()

except Exception as e:
    print(f"❌ ERROR: {e}")
    exit()
