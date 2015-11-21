class EventListener(object):
    def process_event(self, event, data=None):
        pass

    def is_enabled(self):
        return False
