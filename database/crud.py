from sqlalchemy.orm import Session
from database.models import EventLog
from datetime import datetime

def create_event(db: Session, ear: float, mar: float, p: float, y: float, r: float, state: str, perclos: float):
    db_event = EventLog(
        timestamp=datetime.utcnow(),
        ear=ear, mar=mar, head_pitch=p, head_yaw=y, head_roll=r,
        state=state, perclos=perclos
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_recent_events(db: Session, limit: int = 100):
    return db.query(EventLog).order_by(EventLog.timestamp.desc()).limit(limit).all()
