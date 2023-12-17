# main.py

from db.database import SessionLocal, init_db
from db import queries

def main():
    # Initialize the database (create tables)
    init_db()

    # Create a new database session
    db = SessionLocal()

    # Create a new training session
    training_session = queries.create_training_session(db, optimizer='adam', learning_rate=0.001, epochs=10)

    # Create epoch data
    epoch_data = queries.create_epoch_data(db, session_id=training_session.session_id, epoch_number=1, train_loss=0.5, train_accuracy=0.8, val_loss=0.6, val_accuracy=0.75)

    # Close the session
    db.close()

if __name__ == "__main__":
    main()
