from enum import Enum
from core.algorithms import PERCLOSCalculator
class State(Enum):
    ALERT = "ALERT"
    DROWSY_WARNING = "DROWSY_WARNING"
    DROWSY_CRITICAL = "DROWSY_CRITICAL"
    MICROSLEEP = "MICROSLEEP"
class DrowsinessTracker:
    def __init__(self, fps=30):
        self.fps = fps
        self.consecutive_closed_frames = 0
        
        # EXTREME SENSITIVITY THRESHOLDS
        self.warning_threshold = 2      # ~0.06s instant alarm (basically an immediate blink triggers it if they pause)
        self.microsleep_threshold = 8   # ~0.25s for full auto vehicle stop (very aggressive)
        
        self.perclos = PERCLOSCalculator(history_size=fps * 60)
        self.current_state = State.ALERT
        
    def update(self, ear: float, ear_thresh: float) -> State:
        # Increase the physical threshold slightly so half-closed eyes trigger it
        adjusted_thresh = ear_thresh * 1.05 
        is_closed = ear < adjusted_thresh
        perclos_val = self.perclos.update(is_closed)
        
        if is_closed:
            self.consecutive_closed_frames += 1
        else:
            self.consecutive_closed_frames = 0
            
        if self.consecutive_closed_frames >= self.microsleep_threshold:
            self.current_state = State.MICROSLEEP
        elif perclos_val > 0.6 or self.consecutive_closed_frames >= self.warning_threshold * 2:
            self.current_state = State.DROWSY_CRITICAL
        elif perclos_val > 0.4 or self.consecutive_closed_frames >= self.warning_threshold:
            self.current_state = State.DROWSY_WARNING
        else:
            self.current_state = State.ALERT
            
        return self.current_state, perclos_val