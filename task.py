from event_listener import EventListener
from app_events import *
import time


class TaskManager(EventListener):
    def __init__(self, event_bus):
        self.tasks = []
        self.event_bus = event_bus
        self.event_bus.add_listener(self)

    def process_event(self, event, data=None):
        if event == INTERNAL_EVENT_LAUNCH_TASK:
            if data:
                self.add_task(data)

    def is_enabled(self):
        return True

    def add_task(self, task):
        task.event_bus = self.event_bus
        self.event_bus.add_listener(task)
        self.tasks.append(task)

    def update(self):
        self.tasks = filter(lambda task: task.active, self.tasks)
        for active_task in self.tasks:
            active_task.update()


class Task(EventListener):
    def __init__(self):
        self.active = True
        self.event_bus = None

    def update(self):
        pass

    def is_enabled(self):
        return self.active


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

    CANCEL_PATROL_EVENTS = [EVENT_NEXT_MONITOR, EVENT_PREV_MONITOR, INTERNAL_EVENT_COMPONENT_SWITCHED]

    def process_event(self, event, data=None):
        if event in self.CANCEL_PATROL_EVENTS:
            self.active = False
