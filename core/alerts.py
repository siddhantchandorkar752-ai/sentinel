import pygame
import threading
from twilio.rest import Client
from loguru import logger
from config import settings
from core.tracker import State

class AlertSystem:
    def __init__(self):
        pygame.mixer.init()
        # Mocking sounds for compilation
        self.sounds = {
            State.DROWSY_WARNING: None,
            State.DROWSY_CRITICAL: None,
            State.MICROSLEEP: None
        }
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
    def trigger_audio(self, state: State):
        # Implementation to play sound based on state
        logger.info(f"Audio alert triggered for {state.value}")
        
    def trigger_sms(self):
        if not self.twilio_client: return
        try:
            message = self.twilio_client.messages.create(
                body="EMERGENCY: Driver is in a state of critical drowsiness/microsleep.",
                from_=settings.TWILIO_FROM_NUMBER,
                to=settings.EMERGENCY_CONTACT_NUMBER
            )
            logger.info(f"SMS sent: {message.sid}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")

    def escalate(self, state: State):
        threading.Thread(target=self.trigger_audio, args=(state,)).start()
        if state == State.MICROSLEEP or state == State.DROWSY_CRITICAL:
            threading.Thread(target=self.trigger_sms).start()
