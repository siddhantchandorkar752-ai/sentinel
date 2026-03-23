from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class EventLog(Base):
    __tablename__ = "event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ear = Column(Float)
    mar = Column(Float)
    head_pitch = Column(Float)
    head_yaw = Column(Float)
    head_roll = Column(Float)
    state = Column(String)
    perclos = Column(Float)
