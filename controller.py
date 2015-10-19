import sys
import os

import app_events
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


class AppController(Controller):
    def __init__(self, event_bus):
        super(self.__class__, self).__init__(event_bus)
        self.enabled = True
        self.event_map = {app_events.EVENT_QUIT: self.quit_app,
                          app_events.EVENT_SHUTDOWN: self.shutdown_system}

    @staticmethod
    def quit_app(data=None):
        sys.exit(0)

    @staticmethod
    def shutdown_system(data=None):
        os.system('sudo halt')
        sys.exit(0)


class ZoneminderStreamerController(Controller):
    def __init__(self, event_bus, view, overlay, group_tracker_loader):
        super(self.__class__, self).__init__(event_bus)
        self.view = view
        self.overlay = overlay
        self.group_tracker_loader = group_tracker_loader
        self.current_monitor_id = group_tracker_loader.get_current_monitor()
        self.event_map = {app_events.EVENT_NEXT_MONITOR: self.move_to_next_monitor_stream,
                          app_events.EVENT_PREV_MONITOR: self.move_to_prev_monitor_stream}

    def move_to_prev_monitor_stream(self, data=None):
        self.overlay.show_left_arrow = True
        monitor = self.group_tracker_loader.move_to_prev_monitor()
        self.move_to_new_monitor_stream(monitor)

    def move_to_next_monitor_stream(self, data=None):
        self.overlay.show_right_arrow = True
        monitor = self.group_tracker_loader.move_to_next_monitor()
        self.move_to_new_monitor_stream(monitor)

    def move_to_new_monitor_stream(self, monitor):
        if monitor.id != self.current_monitor_id:
            self.view.start_stream(monitor)


class SelectorController(Controller):
    def __init__(self, event_bus, view, selection_handler):
        super(self.__class__, self).__init__(event_bus)
        self.view = view
        self.selection_handler = selection_handler
        self.event_map = {app_events.EVENT_MOUSE_DRAG: self.process_dragging,
                          app_events.EVENT_MOUSE_CLICK: self.process_click}

    def process_dragging(self, data):
        self.view.drag(data[0], data[1])

    def process_click(self, data):
        selection = self.view.process_click(data)
        if selection:
            self.selection_handler.handle_selection(selection)
