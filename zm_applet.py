import os
import pygame

from app_component_manager import AppComponentManager
from app_config import *
from app_context import AppContext
from app_menu_component import MenuSelector, ShutdownPromptSelector
from controller import Controller
from display import PygameDisplay
from event_bus import EventBus
from input_handler import PygameInputHandler
from input_manager import InputManager
from monitor_select_components import GroupSelectorComponent, MonitorSelectorComponent
from monitor_stream_component import MonitorStreamComponent
from startup_component import StartUpComponent
from task_manager import TaskManager
from zoneminder.client import ZoneMinderClient
from zoneminder.group_tracker import ZmGroupTracker


class ZmApplet(object):
    def __init__(self):
        def get_input_handlers(controller, app_config):
            handlers = [PygameInputHandler(controller, app_config)]
            try:
                from pi_input_handler import PiInputHandler

                handlers.append(PiInputHandler(controller, app_config))
            except ImportError:
                print('Unable to import raspberrypi input handler')
            return handlers

        def get_zoneminder_client(app_config):
            zm_client = ZoneMinderClient(app_config.config[SERVER_HOST], app_config.config[SERVER_PORT],
                                         app_config.config[ZM_WEB_PATH], app_config.config[USER_NAME],
                                         app_config.config[PASSWORD], app_config.config[ZMS_WEB_PATH])
            return zm_client

        config = AppConfig()
        event_bus = EventBus()
        client = get_zoneminder_client(config)
        self.app_state = AppState()
        self.app_context = AppContext(config, client, event_bus)

        self.display = PygameDisplay(config)
        self.display.init()
        self.app_context.display_size = self.display.get_display_size()

        zm_stream_component = MonitorStreamComponent(self.app_context)
        group_selector_component = GroupSelectorComponent(self.app_context)
        monitor_selector_component = MonitorSelectorComponent(self.app_context)
        shutdown_prompt_component = ShutdownPromptSelector(self.app_context)
        menu_selector = MenuSelector(self.app_context)
        startup_component = StartUpComponent(self.app_context)
        self.component_manager = AppComponentManager(self.display, event_bus, startup_component, zm_stream_component,
                                                     [group_selector_component, monitor_selector_component,
                                                      shutdown_prompt_component, menu_selector])
        self.input_manager = InputManager(get_input_handlers(event_bus, config))
        self.app_controller = AppController(self.app_context, self.input_manager, self.app_state)
        self.task_manager = TaskManager(event_bus)

    def run(self):
        self.app_controller.activate()
        clock = pygame.time.Clock()
        time_elapsed = 0

        while self.app_state.is_running and not self.app_state.shutdown_system:
            self.input_manager.process_inputs()
            self.task_manager.update()
            self.app_context.event_bus.process_queue()
            self.component_manager.update(time_elapsed)
            self.display.update()
            time_elapsed = clock.tick(10)

        if self.app_state.shutdown_system:
            os.system('sudo halt')
        pygame.quit()


class AppController(Controller):
    def __init__(self, app_context, input_manager, app_state):
        super(AppController, self).__init__(app_context.event_bus)
        self.enabled = True
        self.event_map = {app_events.EVENT_QUIT: self.quit_app,
                          app_events.EVENT_SHUTDOWN: self.shutdown_system,
                          app_events.INTERNAL_EVENT_MONITOR_GROUPS_DATA_LOAD: self.refresh_monitor_group}
        self.app_context = app_context
        self.input_manager = input_manager
        self.first_group_load = False
        self.app_state = app_state

    def quit_app(self, data=None):
        self.app_state.is_running = False

    def shutdown_system(self, data=None):
        self.app_state.shutdown_system = True

    def refresh_monitor_group(self, data):
        def check_and_set_defaults(group_tracker):
            group_name = self.app_context.config.config[STARTING_GROUP_NAME]
            if group_name:
                group_tracker.set_current_group_by_name(group_name)
            monitor_name = self.app_context.config.config[STARTING_MONITOR_NAME]
            if monitor_name:
                group_tracker.set_current_monitor_by_name(monitor_name)

        if not self.first_group_load:
            new_tracker = ZmGroupTracker.create_from_json_api(data[0], data[1])
            if new_tracker:
                self.first_group_load = True
                check_and_set_defaults(new_tracker)
                self.app_context.group_tracker = new_tracker
                if new_tracker.current_monitor:
                    self.app_context.event_bus.publish_event(app_events.INTERNAL_EVENT_SWITCH_TO_MONITOR_STREAM,
                                                             new_tracker.current_monitor)
        else:
            cur_group = self.app_context.group_tracker.current_group
            cur_monitor = self.app_context.group_tracker.current_monitor
            self.app_context.group_tracker.load_from_json_api(data[0], data[1], cur_group, cur_monitor)


class AppState(object):
    def __init__(self):
        self.is_running = True
        self.shutdown_system = False


if __name__ == '__main__':
    app = ZmApplet()
    app.run()
