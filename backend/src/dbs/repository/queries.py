# queries.py

from sqlalchemy.orm import Session
from db.models import TrainingSession, EpochData

def create_training_session(db: Session, optimizer: str, learning_rate: float, epochs: int):
    db_session = TrainingSession(optimizer=optimizer, learning_rate=learning_rate, epochs=epochs)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def create_epoch_data(db: Session, session_id: int, epoch_number: int, train_loss: float, train_accuracy: float, val_loss: float, val_accuracy: float):
    epoch_data = EpochData(
        session_id=session_id,
        epoch_number=epoch_number,
        train_loss=train_loss,
        train_accuracy=train_accuracy,
        val_loss=val_loss,
        val_accuracy=val_accuracy
    )
    db.add(epoch_data)
    db.commit()
    db.refresh(epoch_data)
    return epoch_data

def get_training_sessions(db: Session):
    return db.query(TrainingSession).all()

def get_epoch_data(db: Session, session_id: int):
    return db.query(EpochData).filter(EpochData.session_id == session_id).all()
