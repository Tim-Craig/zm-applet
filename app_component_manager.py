from controller import Controller
from functools import partial
from app_events import INTERNAL_EVENT_RELEASE_COMPONENT


class AppComponentManager(Controller):
    def __init__(self, display, event_bus, default_app_component, app_components):
        def build_event_map():
            self.event_map = {INTERNAL_EVENT_RELEASE_COMPONENT: partial(self.switch_to_component, default_app_component)}
            for app_component in app_components:
                self.event_map[app_component.activation_event] = partial(self.switch_to_component, app_component)

        super(self.__class__, self).__init__(event_bus)
        self.display = display
        self.event_bus = event_bus
        self.default_app_component = default_app_component
        self.app_components = app_components
        self.current_component = default_app_component
        self.current_component.activate()
        self.display.set_view(self.current_component.view)
        self.enabled = True
        build_event_map()

    def update(self):
        self.display.update()

    def switch_to_component(self, app_component, data=None):
        self.current_component.deactivate()
        self.current_component = app_component
        self.current_component.activate(data)
        self.display.set_view(self.current_component.view)
