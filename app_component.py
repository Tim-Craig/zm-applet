from controller import ZoneminderStreamerController, SelectorController
from view import ZoneminderStreamView, ListView, MonitorChangeOverlay
from selection_handler import MethodCallbackSelectionHandler
from app_events import *


class AppComponent(object):
    def __init__(self, app_config, event_bus, activation_event):
        self.app_config = app_config
        self.event_bus = event_bus
        self.activation_event = activation_event
        self.controller = None
        self.view = None
        self.overlay = None

    def activate(self, data=None):
        self.controller.enabled = True

    def deactivate(self):
        self.controller.enabled = False


class ZoneminderStreamComponent(AppComponent):
    def __init__(self, app_config, event_bus, zm_client, group_tracker_loader):
        super(ZoneminderStreamComponent, self).__init__(event_bus, app_config, None)
        self.event_bus = event_bus
        self.group_tracker_loader = group_tracker_loader
        self.activation_event = None
        self.view = ZoneminderStreamView(zm_client, group_tracker_loader, self.stream_release_callback)
        self.overlay = MonitorChangeOverlay()
        self.controller = ZoneminderStreamerController(event_bus, self.view, self.overlay, group_tracker_loader)

    def stream_release_callback(self):
        self.overlay.show_left_arrow = False
        self.overlay.show_right_arrow = False


class SelectorComponent(AppComponent):
    def __init__(self, app_config, event_bus, activation_event, caption, item_list, selection_handler):
        super(SelectorComponent, self).__init__(app_config, event_bus, activation_event)
        self.view = None # The view is created on call activate
        self.controller = None
        self.caption = caption
        self.item_list = item_list
        self.selection_handler = selection_handler

    def activate(self, data=None):
        self.view = ListView(self.caption, self.item_list)
        self.controller = SelectorController(self.event_bus, self.view, self.selection_handler)
        self.event_bus.publish_event(INTERNAL_EVENT_SHOW_MOUSE)
        super(SelectorComponent, self).activate(data)

    def deactivate(self):
        self.event_bus.publish_event(INTERNAL_EVENT_HIDE_MOUSE)
        super(SelectorComponent, self).deactivate()


class BaseZoneminderSelectorComponent(SelectorComponent):
    def __init__(self, app_config, event_bus, group_tracker, activation_event, caption):
        super(BaseZoneminderSelectorComponent, self).__init__(app_config, event_bus, activation_event, caption, None, None)
        self.group_tracker = group_tracker
        self.name_to_ids = None

    def activate(self, data=None):
        self.name_to_ids = {item.name: item.id for item in self.get_items()}
        self.item_list = [item.name for item in self.get_items()]
        self.selection_handler = MethodCallbackSelectionHandler(self.handle_selection)
        super(BaseZoneminderSelectorComponent, self).activate(data)

    def get_items(self):
        pass

    def handle_selection(self, selection):
        pass


class GroupSelectorComponent(BaseZoneminderSelectorComponent):
    def __init__(self, app_config, event_bus, group_tracker):
        super(GroupSelectorComponent, self).__init__(app_config, event_bus, group_tracker, EVENT_OPEN_GROUP_VIEW, 'Select Group')

    def get_items(self):
        return self.group_tracker.groups

    def handle_selection(self, selection):
        id = self.name_to_ids[selection]
        self.group_tracker.set_current_group(id)
        self.event_bus.publish_event(EVENT_OPEN_MONITOR_LIST_VIEW)


class MonitorSelectorComponent(BaseZoneminderSelectorComponent):
    def __init__(self, app_config, event_bus, group_tracker):
        super(MonitorSelectorComponent, self).__init__(app_config, event_bus, group_tracker, EVENT_OPEN_MONITOR_LIST_VIEW, 'Select Monitor')
        self.group_tracker = group_tracker
        self.monitor_name_to_ids = None

    def get_items(self):
        return self.group_tracker.get_current_group_monitors()

    def handle_selection(self, monitor_name):
        id = self.name_to_ids[monitor_name]
        self.group_tracker.set_current_monitor(id)
        self.event_bus.publish_event(INTERNAL_EVENT_RELEASE_COMPONENT)


class ShutdownPromptSelector(SelectorComponent):
    def __init__(self, app_config, event_bus):
        super(ShutdownPromptSelector, self).__init__(app_config, event_bus, EVENT_SHUTDOWN_PROMPT , 'Shutdown?', ['Yes', 'No'], MethodCallbackSelectionHandler(self.handle_selection))

    def handle_selection(self, selection):
        if selection == 'Yes':
            self.event_bus.publish_event(SHUTDOWN)
        else:
            self.event_bus.publish_event(INTERNAL_EVENT_RELEASE_COMPONENT)
