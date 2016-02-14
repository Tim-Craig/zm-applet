import app_config
import app_events
from app_component import AppComponent
from app_events import *
from common_tasks import PatrolTask
from common_views import MessageView
from controller import Controller
from load_monitor_group_task import LoadMonitorGroupsTask
from monitor_stream_task import MonitorStreamTask


class StartUpController(Controller):
    def __init__(self, app_context, view):
        super(StartUpController, self).__init__(app_context.event_bus)
        self.view = view
        self.error_occurred = False
        self.app_context = app_context
        self.event_map = {app_events.INTERNAL_EVENT_MONITOR_GROUPS_DATA_LOAD: self.groups_loaded,
                          app_events.INTERNAL_EVENT_MONITOR_GROUPS_DATA_LOAD_ERROR: self.groups_load_error}

    def groups_loaded(self, data=None):
        if self.app_context.config.get_as_boolean(app_config.PATROL_AT_START_UP):
            self.event_bus.publish_event(INTERNAL_EVENT_LAUNCH_TASK,
                                         (PatrolTask(float(self.app_context.config.config[app_config.PATROL_DELAY]))))
        self.event_bus.publish_event(app_events.INTERNAL_EVENT_RELEASE_COMPONENT)

    ERROR_LOADING_MESSAGE = 'Error connecting, retrying...'

    def groups_load_error(self, data=None):
        if not self.error_occurred:
            self.error_occurred = True
            self.view.set_message(self.ERROR_LOADING_MESSAGE)


STARTUP_MESSAGE = 'Loading ...'


class StartUpComponent(AppComponent):
    def __init__(self, app_context):
        super(StartUpComponent, self).__init__(app_context, None)
        self.view = MessageView(STARTUP_MESSAGE)
        self.controller = StartUpController(app_context, self.view)
        app_context.event_bus.publish_event(INTERNAL_EVENT_LAUNCH_TASK, (LoadMonitorGroupsTask(self.app_context)))
        app_context.event_bus.publish_event(app_events.INTERNAL_EVENT_LAUNCH_TASK,
                                            MonitorStreamTask(self.app_context))
