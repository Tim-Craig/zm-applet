from event_listener import EventListener


class Controller(EventListener):
    def __init__(self, event_bus):
        self.enabled = False
        self.event_map = {}
        self.event_bus = event_bus
        event_bus.add_listener(self)

    def process_event(self, event, data=None):
        if self.enabled:
            if event in self.event_map:
                event_function = self.event_map[event]
                event_function(data)

    def activate(self):
        self.enabled = True

    def deactivate(self):
        self.enabled = False

    def close(self):
        self.deactivate()

    def is_enabled(self):
        return self.enabled
