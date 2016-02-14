from app_component import AppComponent
from app_events import *
from common_views import ListView
from controller import Controller


class SelectorComponent(AppComponent):
    def __init__(self, app_context, activation_event, caption, item_list, selection_handler):
        super(SelectorComponent, self).__init__(app_context, activation_event)
        self.controller = None
        self.caption = caption
        self.item_list = item_list
        self.selection_handler = selection_handler
        self.view = ListView(self.caption, self.item_list)

    def activate(self, data=None):
        self.controller = SelectorController(self.app_context.event_bus, self.view, self.selection_handler)
        self.app_context.event_bus.publish_event(INTERNAL_EVENT_SHOW_MOUSE)
        super(SelectorComponent, self).activate(data)

    def deactivate(self):
        self.app_context.event_bus.publish_event(INTERNAL_EVENT_HIDE_MOUSE)
        super(SelectorComponent, self).deactivate()


class SelectorController(Controller):
    def __init__(self, event_bus, view, selection_handler):
        super(self.__class__, self).__init__(event_bus)
        self.view = view
        self.selection_handler = selection_handler
        self.event_map = {EVENT_MOUSE_DRAG: self.process_dragging,
                          EVENT_MOUSE_CLICK: self.process_click}

    def process_dragging(self, data):
        self.view.drag(data[0], data[1])

    def process_click(self, data):
        selection = self.view.process_click(data)
        if selection:
            self.selection_handler.handle_selection(selection)


class SelectionHandler(object):
    def handle_selection(self, selection):
        pass


class MethodCallbackSelectionHandler(SelectionHandler):
    def __init__(self, method):
        self.method = method

    def handle_selection(self, selection):
        self.method(selection)
