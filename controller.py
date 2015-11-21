import sys
import os

import app_events
from functools import partial
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


LEFT_TOUCH_AREA = [0,0,0.20,1.00]
RIGHT_TOUCH_AREA = [.80,0,0.20,1.00]
MENU_TOUCH_AREA = [.20, 0, .60, .20]
SHUTDOWN_TOUCH_AREA = [.20, .80, .60, .20]

class ZoneminderStreamerController(Controller):
    def __init__(self, event_bus, view, overlay, group_tracker_loader):
        super(self.__class__, self).__init__(event_bus)
        self.view = view
        self.overlay = overlay
        self.group_tracker_loader = group_tracker_loader
        self.current_monitor_id = group_tracker_loader.get_current_monitor()
        self.mouse_area_handler = None
        self.event_map = {app_events.EVENT_NEXT_MONITOR: self.move_to_next_monitor_stream,
                          app_events.INTERNAL_EVENT_NEXT_PATROL_MONITOR: self.move_to_next_monitor_stream,
                          app_events.EVENT_PREV_MONITOR: self.move_to_prev_monitor_stream,
                          app_events.EVENT_MOUSE_CLICK: self.process_click}

    def activate(self):
        def build_mouse_area_mapping():
            areas = [LEFT_TOUCH_AREA, RIGHT_TOUCH_AREA, MENU_TOUCH_AREA, SHUTDOWN_TOUCH_AREA]
            area_actions = [self.move_to_prev_monitor_stream, self.move_to_next_monitor_stream,
                            partial(self.event_bus.publish_event, app_events.EVENT_OPEN_GROUP_VIEW),
                            partial(self.event_bus.publish_event, app_events.EVENT_SHUTDOWN_PROMPT)]
            return MouseAreaMap(self.view.size, areas,area_actions)
        super(ZoneminderStreamerController, self).activate()
        if not self.mouse_area_handler:
            self.mouse_area_handler = build_mouse_area_mapping()


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

    def process_click(self, data=None):
        self.mouse_area_handler.mouse_click(data[0], data[1])


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


class MouseAreaMap(object):
    def __init__(self, screen_size, areas, area_actions):
        def convert_area_to_pixel_area(area):
            pixel_area = [screen_size[0] * area[0], screen_size[1] * area[1], screen_size[0] * area[2],
                          screen_size[1] * area[3]]
            return pixel_area
        self.screen_size = screen_size
        self.areas = areas
        self.area_actions = area_actions
        self.pixel_areas = map(convert_area_to_pixel_area, areas)

    def mouse_click(self, x, y):
        def is_point_in_area(x, y, area):
            is_in_area = True
            is_in_area = is_in_area and (area[0] <= x <= (area[0] + area[2]))
            is_in_area = is_in_area and (area[1] <= y <= (area[1] + area[3]))
            return is_in_area
        for idx, pixel_area in enumerate(self.pixel_areas):
            if is_point_in_area(x, y, pixel_area):
                self.area_actions[idx]()