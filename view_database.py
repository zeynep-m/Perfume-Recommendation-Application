import sqlite3

# Connect to the database
conn = sqlite3.connect('perfumes.db')
cursor = conn.cursor()

# Get column names
cursor.execute("SELECT * FROM perfumes LIMIT 1")
columns = [description[0] for description in cursor.description]

print("="*60)
print("PERFUMES DATABASE")
print("="*60)

# Count total perfumes
cursor.execute("SELECT COUNT(*) FROM perfumes")
total = cursor.fetchone()[0]
print(f"\nTotal perfumes in database: {total}\n")

# Show first 5 perfumes
cursor.execute("SELECT * FROM perfumes LIMIT 5")
rows = cursor.fetchall()

for i, row in enumerate(rows, 1):
    print(f"\n{'='*60}")
    print(f"PERFUME #{i}")
    print('='*60)
    for col_name, value in zip(columns, row):
        print(f"{col_name:20s}: {value}")

print("\n" + "="*60)
print(f"Showing 5 of {total} perfumes")
print("="*60)

conn.close()
