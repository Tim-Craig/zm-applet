import pygame

import app_config
import app_events
import common_controllers
import util
from app_component import AppComponent
from common_views import ArrowDisplay, Button, CurrentTimeLabel, ImageView
from controller import Controller
from view import CompoundView


class MonitorStreamComponent(AppComponent):
    def __init__(self, app_context):
        super(MonitorStreamComponent, self).__init__(app_context, None)
        self.app_context = app_context
        self.activation_event = None
        self.view = ImageView()
        self.overlay = MonitorOverlay(self.left_side_click_callback, self.right_side_click_callback,
                                      self.open_group_view_callback, self.menu_button_callback)
        self.controller = MonitorStreamerController(app_context, self.view, self.overlay,
                                                    app_context.config.config[app_config.MAX_FPS])

    def left_side_click_callback(self):
        self.app_context.event_bus.publish_event(app_events.EVENT_PREV_MONITOR)

    def right_side_click_callback(self):
        self.app_context.event_bus.publish_event(app_events.EVENT_NEXT_MONITOR)

    def open_group_view_callback(self):
        self.app_context.event_bus.publish_event(app_events.EVENT_OPEN_GROUP_VIEW)

    def menu_button_callback(self):
        self.app_context.event_bus.publish_event(app_events.EVENT_OPEN_MENU)


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
                          app_events.INTERNAL_EVENT_NEW_STREAM_FRAME: self.process_new_frame,
                          app_events.INTERNAL_EVENT_STREAM_ERROR_RETRYING: self.display_retry_message}
        common_controllers.add_common_view_controller_methods(self.event_map, self.overlay)

    RETRY_MESSAGE = "Lost connection.  Retrying..."

    def activate(self):
        super(MonitorStreamerController, self).activate()
        self.retry_message_img = util.create_message_image(self.RETRY_MESSAGE, self.image_view.size)

    def close(self):
        super(MonitorStreamerController, self).close()

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
        self.loading_new_image = False
        self.image_view.set_image(self.retry_message_img)

    def open_group_view(self):
        self.event_bus.publish_event(app_events.EVENT_OPEN_GROUP_VIEW)

    def open_menu(self):
        self.event_bus.publish_event(app_events.EVENT_OPEN_MENU)


class MonitorOverlay(CompoundView):
    GROUP_VIEW_BUTTON = "Group/Monitor List"
    MENU_BUTTON = "Open Menu"
    BUTTON_ACTIVATE_TIME = 250
    BUTTON_MAX_AWAKE_TIME = 4000

    def __init__(self,
                 left_side_click_callback,
                 right_side_click_callback,
                 open_group_view_callback,
                 open_menu_callback,
                 arrow_color=(0, 255, 0)):
        self.left_arrow = ArrowDisplay(ArrowDisplay.LEFT_ARROW, left_side_click_callback, arrow_color)
        self.right_arrow = ArrowDisplay(ArrowDisplay.RIGHT_ARROW, right_side_click_callback, arrow_color)
        self.group_view_button = Button(MonitorOverlay.GROUP_VIEW_BUTTON, open_group_view_callback)
        self.group_view_button.enabled = False
        self.menu_button = Button(MonitorOverlay.MENU_BUTTON, open_menu_callback)
        self.menu_button.enabled = False
        self.clock_view = CurrentTimeLabel()
        self.clock_view.enabled = False

        child_views = []
        relative_dimensions = []

        child_views.append(self.left_arrow)
        relative_dimensions.append((0, .50 - .12, .24, .24))

        child_views.append(self.right_arrow)
        relative_dimensions.append((1 - .24, .50 - .12, .24, .24))

        child_views.append(self.group_view_button)
        relative_dimensions.append((.15, .85, .30, .10))

        child_views.append(self.menu_button)
        relative_dimensions.append((.55, .85, .30, .10))

        child_views.append(self.clock_view)
        relative_dimensions.append((0, 0, 1, .15))

        self.buttons_awake_time = 0
        self.buttons_activate_time = 0

        super(MonitorOverlay, self).__init__(child_views, relative_dimensions)

    def show_right_arrow(self):
        self.right_arrow.show_arrow()

    def show_left_arrow(self):
        self.left_arrow.show_arrow()

    def clear_arrows(self):
        self.right_arrow.hide_arrow()
        self.left_arrow.hide_arrow()

    def process_click(self, pos):
        def is_point_in_rect(p, rect):
            max_x = rect[0] + rect[2]
            max_y = rect[1] + rect[3]
            return rect[0] <= p[0] <= max_x and rect[1] <= p[1] <= max_y

        super(MonitorOverlay, self).process_click(pos)
        left_arrow_rect = self.child_actual_rects[0]
        right_arrow_rect = self.child_actual_rects[1]
        if (not is_point_in_rect(pos, left_arrow_rect)) and (not is_point_in_rect(pos, right_arrow_rect)):
            if self.menu_button.enabled:
                self.buttons_awake_time = MonitorOverlay.BUTTON_MAX_AWAKE_TIME
            else:
                self.buttons_activate_time = MonitorOverlay.BUTTON_ACTIVATE_TIME

    def drag(self, drag_start_point, current_pos, delta):
        super(MonitorOverlay, self).drag(drag_start_point, current_pos, delta)
        self._update_button_awake_time()

    def process_pressed(self, pos):
        super(MonitorOverlay, self).process_pressed(pos)
        self._update_button_awake_time()

    def process_press_released(self, pos):
        super(MonitorOverlay, self).process_press_released(pos)
        self._update_button_awake_time()

    def _update_button_awake_time(self):
        if self.buttons_awake_time > 0:
            self.buttons_awake_time = MonitorOverlay.BUTTON_MAX_AWAKE_TIME

    def update(self, time_elapsed):
        super(MonitorOverlay, self).update(time_elapsed)
        if self.buttons_activate_time > 0:
            self.buttons_activate_time = self.buttons_activate_time - time_elapsed
            if self.buttons_activate_time <= 0:
                self.group_view_button.enabled = True
                self.menu_button.enabled = True
                self.clock_view.enabled = True
                self.buttons_awake_time = MonitorOverlay.BUTTON_MAX_AWAKE_TIME
        elif self.buttons_awake_time > 0:
            self.buttons_awake_time = self.buttons_awake_time - time_elapsed
            if self.buttons_awake_time <= 0:
                self.group_view_button.enabled = False
                self.menu_button.enabled = False
                self.clock_view.enabled = False
                self.need_repaint = True
