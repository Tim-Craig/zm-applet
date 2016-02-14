class AppContext(object):
    def __init__(self, config, client, event_bus):
        self.config = config
        self.client = client
        self.event_bus = event_bus
        self.group_tracker = None
        self.display_size = None
