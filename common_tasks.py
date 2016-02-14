import time

from app_events import *
from task import Task


class PatrolTask(Task):
    def __init__(self, interval):
        super(PatrolTask, self).__init__()
        self.interval = interval
        self.last_switch = time.time()
        self.received_first_switch_event = False

    def update(self):
        current_time = time.time()
        if (current_time - self.last_switch) >= self.interval:
            self.last_switch = current_time
            self.event_bus.publish_event(INTERNAL_EVENT_NEXT_PATROL_MONITOR)

    CANCEL_PATROL_EVENTS = [EVENT_NEXT_MONITOR, EVENT_PREV_MONITOR, INTERNAL_EVENT_COMPONENT_SWITCHED]

    def process_event(self, event, data=None):
        # Ignore the first INTERNAL_EVENT_COMPONENT_SWITCHED event so that task doesn't immediately cancel
        if event == INTERNAL_EVENT_COMPONENT_SWITCHED and not self.received_first_switch_event:
            self.received_first_switch_event = True
        elif event in self.CANCEL_PATROL_EVENTS:
            self.alive = False
