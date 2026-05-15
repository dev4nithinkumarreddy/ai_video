import sqlite3
import os

db_path = r"d:\KMEdTech\ai_video\ai-video-generator\backend\ai_video.db"

if not os.path.exists(db_path):
    print(f"Database file not found at: {db_path}")
else:
    print(f"Database found at: {db_path}")
    print(f"File size: {os.path.getsize(db_path)} bytes")
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in database.")
    else:
        print(f"Tables found ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            print(f"\n--- Table: {table_name} ---")

            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Row count: {count}")

            # If there are rows, show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                print("Sample data (first 3 rows):")
                for row in rows:
                    print(f"  {row}")

    conn.close()
