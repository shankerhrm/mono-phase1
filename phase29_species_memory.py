import sqlite3
import json

class SpeciesMemoryDB:
    def __init__(self, db_path="species_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generations (
                    generation INTEGER PRIMARY KEY,
                    fitness REAL,
                    temperature REAL,
                    top_p REAL,
                    heuristic_genes TEXT
                )
            ''')
            conn.commit()

            # Seed generation 0 if empty
            cursor.execute('SELECT COUNT(*) FROM generations')
            if cursor.fetchone()[0] == 0:
                self.record_generation(0, 0, 0.7, 0.9, ["Be concise", "Act biologically"])

    def record_generation(self, generation, fitness, temperature, top_p, heuristic_genes):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO generations (generation, fitness, temperature, top_p, heuristic_genes)
                VALUES (?, ?, ?, ?, ?)
            ''', (generation, fitness, temperature, top_p, json.dumps(heuristic_genes)))
            conn.commit()

    def get_best_traits(self):
        """Returns the traits of the highest-fitness generation to act as the evolutionary parent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT temperature, top_p, heuristic_genes 
                FROM generations 
                ORDER BY fitness DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                return {
                    "temperature": row[0],
                    "top_p": row[1],
                    "heuristic_genes": json.loads(row[2])
                }
            return {"temperature": 0.7, "top_p": 0.9, "heuristic_genes": ["Be concise", "Act biologically"]}

    def get_latest_generation(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(generation) FROM generations')
            val = cursor.fetchone()[0]
            return val if val is not None else 0
