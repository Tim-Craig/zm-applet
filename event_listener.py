class EventListener(object):
    def publish_event(self, event, data=None):
        pass

    def is_enabled(self):
        return False
