from event_listener import EventListener


class Task(EventListener):
    """Base class for background tasks."""

    def __init__(self):
        self.alive = True
        self.event_bus = None

    def update(self):
        pass

    def is_enabled(self):
        return self.alive
