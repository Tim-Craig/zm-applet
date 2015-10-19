class EventBus(object):
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def publish_event(self, event, data=None):
        enabled_listeners = [listener for listener in self.listeners if listener.is_enabled]
        for listener in enabled_listeners:
            listener.process_event(event, data)
