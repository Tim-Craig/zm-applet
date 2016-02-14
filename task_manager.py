from app_events import *
from event_listener import EventListener


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
        self.tasks = filter(lambda task: task.alive, self.tasks)
        for active_task in self.tasks:
            active_task.update()
