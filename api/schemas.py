from pydantic import BaseModel
from datetime import datetime

class EventSchema(BaseModel):
    timestamp: datetime
    ear: float
    mar: float
    head_pitch: float
    head_yaw: float
    head_roll: float
    state: str
    perclos: float
    
    class Config:
        orm_mode = True

class SessionStats(BaseModel):
    total_events: int
    critical_events: int
    avg_perclos: float
