from functools import partial

import pygame

import app_config
import app_events
import util
from app_component import AppComponent
from common_views import ImageView, MonitorChangeOverlay
from controller import Controller

LEFT_TOUCH_AREA = [0, 0, 0.20, 1.00]
RIGHT_TOUCH_AREA = [.80, 0, 0.20, 1.00]
MENU_TOUCH_AREA = [.20, 0, .60, .20]
SHUTDOWN_TOUCH_AREA = [.20, .80, .60, .20]


class MonitorStreamComponent(AppComponent):
    def __init__(self, app_context):
        super(MonitorStreamComponent, self).__init__(app_context, None)
        self.app_context = app_context
        self.activation_event = None
        self.view = ImageView()
        self.overlay = MonitorChangeOverlay()
        self.controller = MonitorStreamerController(app_context, self.view, self.overlay,
                                                    app_context.config.config[app_config.MAX_FPS])


class MonitorStreamerController(Controller):
    def __init__(self, app_context, image_view, overlay, fps):
        super(self.__class__, self).__init__(app_context.event_bus)
        self.retry_message_img = None
        self.loading_new_image = False
        self.image_view = image_view
        self.overlay = overlay
        self.app_context = app_context
        self.fps = fps
        self.current_monitor_id = None
        self.event_map = {app_events.EVENT_NEXT_MONITOR: self.move_to_next_monitor_stream,
                          app_events.INTERNAL_EVENT_NEXT_PATROL_MONITOR: self.move_to_next_monitor_stream,
                          app_events.EVENT_PREV_MONITOR: self.move_to_prev_monitor_stream,
                          app_events.EVENT_MOUSE_CLICK: self.process_click,
                          app_events.INTERNAL_EVENT_NEW_STREAM_FRAME: self.process_new_frame,
                          app_events.INTERNAL_EVENT_STREAM_ERROR_RETRYING: self.display_retry_message}
        self.mouse_area_handler = None

    RETRY_MESSAGE = "Lost connection.  Retrying..."

    def activate(self):
        def build_mouse_area_mapping():
            areas = [LEFT_TOUCH_AREA, RIGHT_TOUCH_AREA, MENU_TOUCH_AREA, SHUTDOWN_TOUCH_AREA]
            area_actions = [self.move_to_prev_monitor_stream, self.move_to_next_monitor_stream,
                            partial(self.event_bus.publish_event, app_events.EVENT_OPEN_GROUP_VIEW),
                            partial(self.event_bus.publish_event, app_events.EVENT_OPEN_MENU)]
            return MouseAreaMap(self.image_view.size, areas, area_actions)

        super(MonitorStreamerController, self).activate()
        if not self.mouse_area_handler:
            self.mouse_area_handler = build_mouse_area_mapping()
        self.retry_message_img = util.create_message_image(self.RETRY_MESSAGE, self.image_view.size)

    def close(self):
        super(MonitorStreamerController, self).close()
        self.streamer.close()

    def handle_next_stream_image(self, image):
        self.new_image_frame_listener()
        self.image_view.image = image

    def move_to_prev_monitor_stream(self, data=None):
        if not self.loading_new_image:
            self.overlay.show_left_arrow()
            self.loading_new_image = True
            monitor = self.app_context.group_tracker.move_to_prev_monitor()
            self.current_monitor_id = monitor.id
            self.event_bus.publish_event(app_events.INTERNAL_EVENT_SWITCH_TO_MONITOR_STREAM, monitor)

    def move_to_next_monitor_stream(self, data=None):
        if not self.loading_new_image:
            self.overlay.show_right_arrow()
            self.loading_new_image = True
            monitor = self.app_context.group_tracker.move_to_next_monitor()
            self.current_monitor_id = monitor.id
            self.event_bus.publish_event(app_events.INTERNAL_EVENT_SWITCH_TO_MONITOR_STREAM, monitor)

    def process_new_frame(self, data):
        if data[1] == self.current_monitor_id:
            self.overlay.clear_arrows()
            self.loading_new_image = False
        image = pygame.image.load(data[0]).convert()
        self.image_view.set_image(image)

    def display_retry_message(self, data=None):
        self.overlay.clear_arrows()
        self.image_view.set_image(self.retry_message_img)

    def process_click(self, data=None):
        self.mouse_area_handler.mouse_click(data[0], data[1])


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
