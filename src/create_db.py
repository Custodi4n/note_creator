import sqlite3

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            reminder_date TEXT NOT NULL,
            reminder_time TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()
