import sqlite3

conn = sqlite3.connect("auth.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS licenses (
    account TEXT,
    server TEXT,
    expiry INTEGER,
    enabled INTEGER
)
""")

conn.commit()
conn.close()
