from app_events import *
from selector_component import MethodCallbackSelectionHandler, SelectorComponent


class BaseZoneminderSelectorComponent(SelectorComponent):
    def __init__(self, app_context, activation_event, caption):
        super(BaseZoneminderSelectorComponent, self).__init__(app_context, activation_event, caption, None, None)
        self.app_context = app_context
        self.name_to_ids = None

    def activate(self, data=None):
        self.name_to_ids = {item.name: item.id for item in self.get_items()}
        self.item_list = [item.name for item in self.get_items()]
        self.selection_handler = MethodCallbackSelectionHandler(self.handle_selection)
        self.view.set_item_list(self.item_list)
        super(BaseZoneminderSelectorComponent, self).activate(data)

    def get_items(self):
        pass

    def handle_selection(self, selection):
        pass


class GroupSelectorComponent(BaseZoneminderSelectorComponent):

    def __init__(self, app_context):
        super(GroupSelectorComponent, self).__init__(app_context, EVENT_OPEN_GROUP_VIEW,
                                                     'Select Group')

    def get_items(self):
        items = self.app_context.group_tracker.groups
        return items

    def handle_selection(self, selection):
        group_id = self.name_to_ids[selection]
        self.app_context.group_tracker.set_current_group(group_id)
        self.app_context.event_bus.publish_event(EVENT_OPEN_MONITOR_LIST_VIEW)


class MonitorSelectorComponent(BaseZoneminderSelectorComponent):
    def __init__(self, app_context):
        super(MonitorSelectorComponent, self).__init__(app_context, EVENT_OPEN_MONITOR_LIST_VIEW, 'Select Monitor')
        self.monitor_name_to_ids = None

    def get_items(self):
        return self.app_context.group_tracker.get_current_group_monitors()

    def handle_selection(self, monitor_name):
        monitor_id = self.name_to_ids[monitor_name]
        self.app_context.group_tracker.set_current_monitor(monitor_id)
        self.app_context.event_bus.publish_event(INTERNAL_EVENT_RELEASE_COMPONENT)
        self.app_context.event_bus.publish_event(INTERNAL_EVENT_SWITCH_TO_MONITOR_STREAM,
                                                 self.app_context.group_tracker.current_monitor)
