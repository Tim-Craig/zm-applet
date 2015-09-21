import pygame
import pygame.event
from pygame.locals import *
import sys
import types
import time
import app_events


class InputHandler(object):
    def __init__(self, event_bus, app_config):
        self.event_bus = event_bus
        self.app_config = app_config

    def check_input_commands(self):
        pass


class InputTracker(object):
    def __init__(self, app_config, input_config_label_mapping):
        event_to_label_mapping = app_config.get_event_configs_assigned_to_input_labels(
            input_config_label_mapping.keys())
        self.single_input_events = {}
        self.multi_input_events = {}
        for event, label_values in event_to_label_mapping.iteritems():
            for label_value in label_values:
                if isinstance(label_value, types.StringTypes):
                    self.single_input_events[input_config_label_mapping[label_value]] = event
                else:
                    mapped_label_values = [input_config_label_mapping[label] for label in label_value]
                    self.multi_input_events[input_config_label_mapping[label_value[0]]] = (event, mapped_label_values)

    def get_triggered_events(self, event_inputs):
        triggered_events = set()
        for event_input in event_inputs:
            if event_input in self.single_input_events:
                triggered_events.add(self.single_input_events[event_input])
            if event_input in self.multi_input_events:
                event, multi_input_set = self.multi_input_events[event_input]
                non_matching_inputs = filter(lambda x: x not in event_inputs, multi_input_set)
                if len(non_matching_inputs) == 0:
                    triggered_events.add(event)
        return triggered_events


CLICK_EXPIRE = 1
DRAG_LIMIT = 7

class MouseEventTracker(object):
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.mouse_down = False
        self.mouse_down_time = 0
        self.drag_start = None
        self.is_dragging = False
        self.total_drag = 0

    def process_mouse_down(self):
        self.mouse_down = True
        self.mouse_down_time = time.time()
        self.drag_start = pygame.mouse.get_pos()
        # call now so next call will return drag move delta
        pygame.mouse.get_rel()
        self.total_drag = 0

    def process_mouse_up(self):
        def is_within_expire_time():
            return (mouse_up_time - self.mouse_down_time) <= CLICK_EXPIRE
        def is_within_drag_limit():
            return self.total_drag <= DRAG_LIMIT
        self.mouse_down = False
        mouse_up_time = time.time()
        if is_within_expire_time() and is_within_drag_limit():
            self.event_bus.publish_event(app_events.EVENT_MOUSE_CLICK, pygame.mouse.get_pos())
        self.mouse_down_time = 0
        self.is_dragging = False

    def process_mouse_move(self):
        mouse_rel_movement = pygame.mouse.get_rel()
        if self.mouse_down and mouse_rel_movement != (0,0):
            self.total_drag += abs(mouse_rel_movement[1])
            self.event_bus.publish_event(app_events.EVENT_MOUSE_DRAG, (self.drag_start, mouse_rel_movement))
            self.is_dragging = True


pygame_key_mapping = {'escape': K_ESCAPE, 'left': K_LEFT, 'right': K_RIGHT, 'space': K_SPACE, 's': K_s}


class PygameInputHandler(InputHandler):
    def __init__(self, event_bus, app_config):
        super(self.__class__, self).__init__(event_bus, app_config)
        self.mouse_tracker = MouseEventTracker(event_bus)
        self.input_trigger = InputTracker(app_config, pygame_key_mapping)

    def check_input_commands(self):
        key_events = []
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                key_events.append(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                self.mouse_tracker.process_mouse_down()
            elif event.type == MOUSEBUTTONUP:
                self.mouse_tracker.process_mouse_up()
            elif event.type == MOUSEMOTION:
                self.mouse_tracker.process_mouse_move()

        triggered_events = self.input_trigger.get_triggered_events(key_events)
        for triggered_event in triggered_events:
            self.event_bus.publish_event(triggered_event)
