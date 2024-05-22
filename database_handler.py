import sqlite3
import sqlite_vss

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.enable_load_extension(True)
        sqlite_vss.load(conn=self.connection)

    def close(self):
        if self.connection:
            self.connection.close()

    def search_recipes(self, serialized_embedding: bytes, limit: int = 3):
        query = """
        SELECT recipes.*, recipes_vec.distance
        FROM recipes_vec
        JOIN recipes ON recipes_vec.rowid = recipes.rowid
        WHERE vss_search(recipes_vec.steps_vec, vss_search_params(?, 10))
        ORDER BY recipes_vec.distance
        LIMIT ?;
        """
        return self.connection.execute(query, (serialized_embedding, limit)).fetchall()
