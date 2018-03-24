import time

from app_events import *
from task import Task


class PatrolTask(Task):
    def __init__(self, interval):
        super(PatrolTask, self).__init__()
        self.interval = interval
        self.last_switch = time.time()

    def update(self):
        current_time = time.time()
        if (current_time - self.last_switch) >= self.interval:
            self.last_switch = current_time
            self.event_bus.publish_event(INTERNAL_EVENT_NEXT_PATROL_MONITOR)

    CANCEL_PATROL_EVENTS = [EVENT_NEXT_MONITOR, EVENT_PREV_MONITOR, EVENT_OPEN_GROUP_VIEW, EVENT_OPEN_MENU]

    def process_event(self, event, data=None):
        if event in self.CANCEL_PATROL_EVENTS:
            self.alive = False
