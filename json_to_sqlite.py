import json
import sqlite3

# Load the JSON data
with open('perfumes.json', 'r') as file:
    perfumes_data = json.load(file)

# Create SQLite database connection
conn = sqlite3.connect('perfumes.db')
cursor = conn.cursor()

# Create the perfumes table
cursor.execute('''
CREATE TABLE IF NOT EXISTS perfumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    perfume TEXT,
    gender TEXT,
    intensity TEXT,
    ingredients_notes TEXT,
    season TEXT,
    concept TEXT,
    longevity TEXT,
    collection TEXT,
    classification TEXT,
    subfamily TEXT
)
''')

# Insert data from JSON into the database
for perfume in perfumes_data:
    cursor.execute('''
    INSERT INTO perfumes (
        perfume, gender, intensity, ingredients_notes, 
        season, concept, longevity, collection, 
        classification, subfamily
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        perfume['Perfume'],
        perfume['Gender'],
        perfume['Intensity'],
        perfume['Ingredients_Notes'],
        perfume['Season'],
        perfume['Concept'],
        perfume['Longevity'],
        perfume['Collection'],
        perfume['Classification'],
        perfume['Subfamily']
    ))

# Commit changes and close connection
conn.commit()
conn.close()

print("Database created successfully!")
