from event_listener import EventListener


class Task(EventListener):
    def __init__(self):
        self.alive = True
        self.event_bus = None

    def update(self):
        pass

    def is_enabled(self):
        return self.alive
