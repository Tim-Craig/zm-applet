class EventBus(object):
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def publish_event(self, event):
        for listener in self.listeners:
            listener.process_event(event)
