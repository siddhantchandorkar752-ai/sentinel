from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from database.models import Base
from api.schemas import EventSchema, SessionStats
from database.crud import get_recent_events

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health")
def read_health():
    return {"status": "ok"}

@router.get("/stats", response_model=SessionStats)
def read_stats(db: Session = Depends(get_db)):
    events = get_recent_events(db, limit=1000)
    total = len(events)
    critical = sum(1 for e in events if e.state in ['DROWSY_CRITICAL', 'MICROSLEEP'])
    avg_p = sum(e.perclos for e in events) / total if total > 0 else 0.0
    return SessionStats(total_events=total, critical_events=critical, avg_perclos=avg_p)

@router.get("/session", response_model=list[EventSchema])
def read_session(db: Session = Depends(get_db), limit: int = 10):
    return get_recent_events(db, limit=limit)
