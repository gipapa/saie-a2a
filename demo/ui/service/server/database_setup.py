import sqlite3

def create_database():
    """Creates the users.db database and the users table."""
    conn = None  # Initialize conn to None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                agent_settings TEXT
            )
        ''')

        conn.commit()
        print("Database and table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating database or table: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()
