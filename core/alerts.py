import threading
import time
import os
from loguru import logger
from config import settings
from core.tracker import State
from twilio.rest import Client
try:
    import winsound
except ImportError:
    winsound = None
class AlertSystem:
    def __init__(self):
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            except Exception as e:
                logger.error(f"Twilio setup failed: {e}")
                
        self.alarm_playing = False
        self.vehicle_stopped = False
        self.sms_sent = False
        self.alarm_thread = None
    def _play_alarm_loop(self):
        while self.alarm_playing:
            if winsound:
                winsound.Beep(1000, 500) # 1000Hz for 500ms
            else:
                logger.warning("BEEP BEEP BEEP (Audio alarm ringing)")
                time.sleep(0.5)
    def trigger_sms(self):
        if not self.twilio_client or self.sms_sent: return
        try:
            message = self.twilio_client.messages.create(
                body="EMERGENCY: Driver is critically drowsy. Vehicle is automatically pulling over.",
                from_=settings.TWILIO_FROM_NUMBER,
                to=settings.EMERGENCY_CONTACT_NUMBER
            )
            logger.info(f"SMS sent: {message.sid}")
            self.sms_sent = True
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
    def initiate_safe_stop(self):
        if not self.vehicle_stopped:
            self.vehicle_stopped = True
            logger.critical("🚨 EMERGENCY PROTOCOL TRIGGERED 🚨")
            logger.critical("Scanning for nearest safe area...")
            time.sleep(2.0)
            logger.critical("Safe area located. Executing automatic gradual stop...")
            time.sleep(3.0)
            logger.critical("Vehicle has successfully parked in safe area. DO NOT DRIVE.")
    def update_state(self, state: State):
        # 1. Instant alarm handling
        if state in [State.DROWSY_WARNING, State.DROWSY_CRITICAL, State.MICROSLEEP]:
            if not self.alarm_playing:
                logger.warning("DROWSINESS DETECTED: Ringing continuous alarm INSTANTLY!")
                self.alarm_playing = True
                self.alarm_thread = threading.Thread(target=self._play_alarm_loop, daemon=True)
                self.alarm_thread.start()
        else:
            if self.alarm_playing:
                logger.success("DRIVER ALERT: Eyes opened. Stopping the alarm.")
                self.alarm_playing = False # Loop condition breaks
                if self.alarm_thread:
                    self.alarm_thread.join(timeout=1.0)
        
        # 2. Vehicle stopping mechanisms for critical states
        if state in [State.DROWSY_CRITICAL, State.MICROSLEEP]:
            if not self.vehicle_stopped:
                threading.Thread(target=self.initiate_safe_stop, daemon=True).start()
                threading.Thread(target=self.trigger_sms, daemon=True).start()
