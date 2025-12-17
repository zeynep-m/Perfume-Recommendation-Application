import sqlite3
import json
import os


class PerfumeDatabase:
    """Database class for managing perfume data"""
    
    def __init__(self, db_name="perfumes.db"):
        self.db_name = db_name
        self.initialize_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def table_exists(self):
        """Check if the perfumes table exists and has data"""
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='perfumes'")
                if cur.fetchone() is None:
                    return False
                # Check if table has data
                cur.execute("SELECT COUNT(*) FROM perfumes")
                count = cur.fetchone()[0]
                return count > 0
        except sqlite3.OperationalError:
            return False

    def initialize_database(self):
        """Initialize database from JSON if table doesn't exist or is empty"""
        if self.table_exists():
            return  # Table already exists and has data

        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file = os.path.join(script_dir, 'perfumes.json')
        
        if not os.path.exists(json_file):
            print(f"Warning: {json_file} not found. Database cannot be initialized.")
            return  # Can't initialize without JSON file

        # Load JSON data
        with open(json_file, 'r') as file:
            perfumes_data = json.load(file)

        # Create table and insert data
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Create table
            cur.execute('''
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
                subfamily TEXT,
                sources TEXT
            )
            ''')
            
            # Insert data from JSON
            for perfume in perfumes_data:
                cur.execute('''
                INSERT INTO perfumes (
                    perfume, gender, intensity, ingredients_notes, 
                    season, concept, longevity, collection, 
                    classification, subfamily, sources
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
                    perfume['Subfamily'],
                    perfume['Sources']
                ))
            
            conn.commit()
            print("Database initialized from perfumes.json")

    def get_perfumes(self):
        """Retrieve all perfumes from the database"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, perfume, gender, intensity, ingredients_notes, collection, season, concept, classification, longevity FROM perfumes")
            return cur.fetchall()

    def get_perfume_details(self, perfume_id):
        """Retrieve full details of a specific perfume"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM perfumes WHERE id=?", (perfume_id,))
            return cur.fetchone()

    def get_total_count(self):
        """Get total number of perfumes in database"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM perfumes")
            return cur.fetchone()[0]

    def delete_perfume(self, perfume_id):
        """Delete a perfume by ID"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM perfumes WHERE id=?", (perfume_id,))

    def update_perfume(self, perfume_id, perfume, gender, intensity, ingredients_notes, 
                      season, concept, longevity, collection, classification, subfamily, sources):
        """Update a perfume record"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            UPDATE perfumes 
            SET perfume=?, gender=?, intensity=?, ingredients_notes=?, 
                season=?, concept=?, longevity=?, collection=?, 
                classification=?, subfamily=?, sources=?
            WHERE id=?
            """, (perfume, gender, intensity, ingredients_notes, season, concept, 
                  longevity, collection, classification, subfamily, sources, perfume_id))

    def add_perfume(self, perfume, gender, intensity, ingredients_notes, 
                   season, concept, longevity, collection, classification, subfamily, sources):
        """Add a new perfume"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO perfumes (perfume, gender, intensity, ingredients_notes, 
                                season, concept, longevity, collection, 
                                classification, subfamily, sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (perfume, gender, intensity, ingredients_notes, season, concept, 
                  longevity, collection, classification, subfamily, sources))

    def search_perfumes(self, search_term):
        """Search perfumes by name, gender, or classification"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            query = """
            SELECT id, perfume, gender, intensity, ingredients_notes, collection, season, concept, classification, longevity 
            FROM perfumes 
            WHERE perfume LIKE ? OR gender LIKE ? OR classification LIKE ? OR ingredients_notes LIKE ? OR season LIKE ?
            """
            search_param = f"%{search_term}%"
            cur.execute(query, (search_param, search_param, search_param, search_param, search_param))
            return cur.fetchall()

    def get_statistics(self):
        """Get statistics about perfumes in the database"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Total count
            cur.execute("SELECT COUNT(*) FROM perfumes")
            total = cur.fetchone()[0]
            
            # Count by gender
            cur.execute("SELECT gender, COUNT(*) FROM perfumes GROUP BY gender ORDER BY COUNT(*) DESC")
            gender_counts = cur.fetchall()
            
            # Count by intensity
            cur.execute("SELECT intensity, COUNT(*) FROM perfumes GROUP BY intensity ORDER BY COUNT(*) DESC")
            intensity_counts = cur.fetchall()
            
            # Count by classification
            cur.execute("SELECT classification, COUNT(*) FROM perfumes GROUP BY classification ORDER BY COUNT(*) DESC LIMIT 5")
            classification_counts = cur.fetchall()
            
            return {
                'total': total,
                'gender': gender_counts,
                'intensity': intensity_counts,
                'classification': classification_counts
            }


if __name__ == '__main__':
    db = PerfumeDatabase()
    print("Database initialized.")
