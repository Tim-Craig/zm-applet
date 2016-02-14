from event_listener import EventListener
from app_events import EVENT_QUIT
import time
import threading


class InputManager(object):
    def __init__(self, input_handlers):
        self.input_handlers = input_handlers

    def process_inputs(self):
        for handler in self.input_handlers:
            handler.check_input_commands()
