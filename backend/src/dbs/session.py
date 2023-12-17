import sqlite3

def create_database():
    conn = sqlite3.connect('training_history.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TrainingSession (
            session_id INTEGER PRIMARY KEY,
            start_time TEXT,
            end_time TEXT,
            optimizer TEXT,
            learning_rate REAL,
            epochs INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS EpochData (
            epoch_id INTEGER PRIMARY KEY,
            session_id INTEGER,
            epoch_number INTEGER,
            train_loss REAL,
            train_accuracy REAL,
            val_loss REAL,
            val_accuracy REAL,
            FOREIGN KEY (session_id) REFERENCES TrainingSession (session_id)
        )
    ''')

    conn.commit()
    conn.close()

create_database()
