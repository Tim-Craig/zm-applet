from app_config import PATROL_DELAY
from app_events import *
from common_tasks import PatrolTask
from selector_component import MethodCallbackSelectionHandler, SelectorComponent


class MenuSelector(SelectorComponent):
    MENU_ITEM_CYCLE_MODE = 'Cycle Mode'
    MENU_ITEM_SHUTDOWN_SYSTEM = 'Shutdown System'
    MENU_ITEM_RETURN = 'Return'

    def __init__(self, app_context):
        super(MenuSelector, self).__init__(app_context, EVENT_OPEN_MENU, '',
                                           [MenuSelector.MENU_ITEM_CYCLE_MODE, MenuSelector.MENU_ITEM_SHUTDOWN_SYSTEM,
                                            MenuSelector.MENU_ITEM_RETURN],
                                           MethodCallbackSelectionHandler(self.handle_selection))

    def handle_selection(self, selection):
        if selection == MenuSelector.MENU_ITEM_CYCLE_MODE:
            self.app_context.event_bus.publish_event(INTERNAL_EVENT_RELEASE_COMPONENT)
            self.app_context.event_bus.publish_event(INTERNAL_EVENT_LAUNCH_TASK,
                                                     PatrolTask(float(self.app_context.config.config[PATROL_DELAY])))
        elif selection == MenuSelector.MENU_ITEM_SHUTDOWN_SYSTEM:
            self.app_context.event_bus.publish_event(EVENT_SHUTDOWN_PROMPT)
        else:
            self.app_context.event_bus.publish_event(INTERNAL_EVENT_RELEASE_COMPONENT)


class ShutdownPromptSelector(SelectorComponent):
    def __init__(self, app_context):
        super(ShutdownPromptSelector, self).__init__(app_context, EVENT_SHUTDOWN_PROMPT, 'Shutdown?',
                                                     ['Yes', 'No'],
                                                     MethodCallbackSelectionHandler(self.handle_selection))

    def handle_selection(self, selection):
        if selection == 'Yes':
            self.app_context.event_bus.publish_event(EVENT_SHUTDOWN)
        else:
            self.app_context.event_bus.publish_event(INTERNAL_EVENT_RELEASE_COMPONENT)
