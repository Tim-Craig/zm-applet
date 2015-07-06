import pygame
import pygame.event
from pygame.locals import *
import sys
import types


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
                    self.multi_input_events[input_config_label_mapping[label_value[0]]] = (event, label_value)

    def get_triggered_events(self, event_inputs):
        triggered_events = set()
        for event_input in event_inputs:
            if event_input in self.single_input_events:
                triggered_events.add(self.single_input_events[event_input])
            if event_input in self.multi_input_events:
                event, multi_input_set = self.multi_input_events[event_input]
                non_matching_inputs = filter(lambda x: x in event_inputs, multi_input_set)
                if len(non_matching_inputs) == 0:
                    triggered_events.add(event)
        return triggered_events


pygame_key_mapping = {'escape': K_ESCAPE, 'left': K_LEFT, 'right': K_RIGHT}


class PygameInputHandler(InputHandler):
    def __init__(self, event_bus, app_config):
        super(self.__class__, self).__init__(event_bus, app_config)
        self.input_trigger = InputTracker(app_config, pygame_key_mapping)

    def check_input_commands(self):
        key_events = []
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                key_events.append(event.key)

        triggered_events = self.input_trigger.get_triggered_events(key_events)
        for triggered_event in triggered_events:
            self.event_bus.publish_event(triggered_event)
