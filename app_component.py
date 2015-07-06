from controller import ZoneminderStreamerController, GroupSelectorController
from view import ZoneminderStreamView, ListView
from app_events import *


class AppComponent(object):
    def __init__(self, app_config, event_bus):
        self.app_config = app_config
        self.event_bus = event_bus
        self.activation_event = None
        self.controller = None
        self.view = None

    def set_enabled(self, is_enabled):
        self.controller.enabled = is_enabled


class ZoneminderStreamComponent(AppComponent):
    def __init__(self, app_config, event_bus, zm_client, group_tracker_loader):
        super(self.__class__, self).__init__(event_bus, app_config)
        self.group_tracker_loader = group_tracker_loader
        self.activation_event = None
        self.view = ZoneminderStreamView(zm_client, group_tracker_loader)
        self.controller = ZoneminderStreamerController(event_bus, self.view, group_tracker_loader)


class GroupSelectorComponent(AppComponent):
    def __init__(self, app_config, event_bus, group_tracker_loader):
        super(self.__class__, self).__init__(event_bus, app_config)
        self.view = ListView()
        self.group_tracker_loader = group_tracker_loader
        self.controller = GroupSelectorController(event_bus)
        self.activation_event = EVENT_OPEN_GROUP_VIEW
