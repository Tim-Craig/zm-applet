import sys
import os


class Controller(object):
    def __init__(self, event_bus):
        self.enabled = False
        self.event_map = {}
        event_bus.add_listener(self)

    def process_event(self, event):
        if self.enabled:
            if event in self.event_map:
                event_function = self.event_map[event]
                event_function()


class AppController(Controller):
    def __init__(self, event_bus):
        super(self.__class__, self).__init__(event_bus)
        self.event_map = {'quit': self.quit_app,
                          'shutdown': self.shutdown_system}

    @staticmethod
    def quit_app():
        sys.exit(0)

    @staticmethod
    def shutdown_system():
        os.system('sudo halt')
        sys.exit(0)


class ZoneminderStreamerController(Controller):
    def __init__(self, event_bus, view, group_tracker_loader):
        super(self.__class__, self).__init__(event_bus)
        self.view = view
        self.group_tracker_loader = group_tracker_loader
        self.current_monitor_id = group_tracker_loader.get_current_monitor()
        self.event_map = {'prev_monitor': self.move_to_prev_monitor_stream,
                          'next_monitor': self.move_to_next_monitor_stream}

    def move_to_prev_monitor_stream(self):
        monitor = self.group_tracker_loader.move_to_prev_monitor()
        self.move_to_new_monitor_stream(monitor)

    def move_to_next_monitor_stream(self):
        monitor = self.group_tracker_loader.move_to_next_monitor()
        self.move_to_new_monitor_stream(monitor)

    def move_to_new_monitor_stream(self, monitor):
        if monitor.id != self.current_monitor_id:
            self.view.start_stream(monitor)


class GroupSelectorController(Controller):
    def __init__(self, event_bus):
        super(self.__class__, self).__init__(event_bus)
        self.event_map = {}