from app_component import AppComponent
from app_events import EVENT_SHOW_CLOCK
from view import View


class ClockComponent(AppComponent):
    def __init__(self, app_context):
        super(app_context, EVENT_SHOW_CLOCK)
        self.app_context = app_context
        self.controller = None
        self.view = None
        self.overlay = None


class ClockView(View):
    def __init__(self):
        super(ClockView, self).__init__()

    def start_view(self, size):
        self.size = size

    def paint(self, display):
        pass

    def close(self):
        pass
