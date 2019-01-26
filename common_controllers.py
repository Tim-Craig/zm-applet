from functools import partial

from app_events import *


def add_common_view_controller_methods(controller_event_map, view):
    controller_event_map[INTERNAL_EVENT_MOUSE_DRAG] = partial(process_dragging, view)
    controller_event_map[INTERNAL_EVENT_MOUSE_DOWN] = partial(process_mouse_down, view)
    controller_event_map[INTERNAL_EVENT_MOUSE_UP] = partial(process_mouse_up, view)
    controller_event_map[INTERNAL_EVENT_MOUSE_CLICK] = partial(process_click, view)


def process_dragging(view, event_data):
    view.drag(event_data[0], event_data[1], event_data[2])


def process_mouse_down(view, event_data):
    view.process_pressed(event_data)


def process_mouse_up(view, event_data):
    view.process_press_released(event_data)


def process_click(view, event_data):
    view.process_click(event_data)
