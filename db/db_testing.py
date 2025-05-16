# import sqlite3
#
# # Connect to the database
# conn = sqlite3.connect('social_media.db')
# cursor = conn.cursor()
#
# # Get all table names
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = [row[0] for row in cursor.fetchall()]
#
# if not tables:
#     print("No tables found in the database.")
# else:
#     print(f"Found tables: {', '.join(tables)}\n")
#
#     for table in tables:
#         print(f"🔍 Checking table: {table}")
#
#         # Count total entries
#         cursor.execute(f"SELECT COUNT(*) FROM {table};")
#         total_count = cursor.fetchone()[0]
#         print(f"📌 Total rows: {total_count}")
#
#         # Get column names
#         cursor.execute(f"PRAGMA table_info({table});")
#         columns = [col[1] for col in cursor.fetchall()]
#
#         # Check for 'label' column
#         if "label" in columns:
#             try:
#                 cursor.execute(f"SELECT label, COUNT(*) FROM {table} GROUP BY label;")
#                 label_counts = cursor.fetchall()
#                 print("✅ Label distribution:")
#                 for label, count in label_counts:
#                     print(f"   Label {label}: {count} entries")
#             except Exception as e:
#                 print(f"⚠️  Error reading labels in table {table}: {e}")
#         else:
#             print("⚠️  No 'label' column found in this table.")
#
#         # Show sample data
#         cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
#         rows = cursor.fetchall()
#         print("📄 Top 5 rows:")
#         for row in rows:
#             print("   ", dict(zip(columns, row)))
#
#         print("-" * 60)
#
# # Close the connection
# conn.close()

import sqlite3

conn = sqlite3.connect('social_media.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:", tables)
conn.close()

