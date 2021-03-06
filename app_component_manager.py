from functools import partial

from app_events import *
from controller import Controller


class AppComponentManager(Controller):
    """Manages the components of the applet.  Primarily handles the switching of components"""

    def __init__(self, display, event_bus, initial_app_component, default_app_component, app_components):
        def build_event_map():
            self.event_map = {
                INTERNAL_EVENT_RELEASE_COMPONENT: partial(self.switch_to_component, default_app_component),
                EVENT_QUIT: self.close, EVENT_SHUTDOWN: self.close}
            for app_component in app_components:
                self.event_map[app_component.activation_event] = partial(self.switch_to_component, app_component)

        super(self.__class__, self).__init__(event_bus)
        self.display = display
        self.event_bus = event_bus
        self.initial_app_component = initial_app_component
        self.default_app_component = default_app_component
        self.app_components = app_components
        self.current_component = None
        self.switch_to_component(initial_app_component)
        self.activate()
        build_event_map()

    def switch_to_component(self, app_component, data=None):
        if self.current_component:
            self.current_component.deactivate()
        self.current_component = app_component
        self.display.set_view(self.current_component.view)
        self.display.set_overlay(self.current_component.overlay)
        self.current_component.activate(data)
        self.event_bus.publish_event(INTERNAL_EVENT_COMPONENT_SWITCHED)

    def close(self, data=None):
        if self.current_component:
            self.current_component.deactivate()
            self.current_component = None

    def update(self, time_elapsed):
        if self.current_component:
            self.current_component.update(time_elapsed)
