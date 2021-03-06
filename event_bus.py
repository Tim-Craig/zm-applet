class EventBus(object):
    def __init__(self):
        self.listeners = []
        self.event_queue = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def publish_event(self, event, data=None):
        self.event_queue.append((event, data))

    def process_queue(self):
        event_count = len(self.event_queue)
        if event_count > 0:
            events = self.event_queue[0:event_count]
            del self.event_queue[0:event_count]
            enabled_listeners = [listener for listener in self.listeners if listener.is_enabled()]
            for event, data in events:
                for listener in enabled_listeners:
                    listener.process_event(event, data)
