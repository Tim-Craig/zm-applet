import time

from app_component import ZoneminderStreamComponent, GroupSelectorComponent, MonitorSelectorComponent, \
    ShutdownPromptSelector
from app_component_manager import AppComponentManager
from app_config import *
from display import PygameDisplay
from event_bus import EventBus
from zoneminder.client import ZoneMinderClient
from zoneminder.group_tracker import RefreshingZmGroupTracker
from controller import AppController
from input_handler import PygameInputHandler


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
            client = ZoneMinderClient(app_config.config[SERVER_HOST], app_config.config[SERVER_PORT],
                                      app_config.config[ZM_WEB_PATH], app_config.config[USER_NAME],
                                      app_config.config[PASSWORD], app_config.config[ZMS_WEB_PATH])
            return client

        self.config = AppConfig()
        self.event_bus = EventBus()

        self.display = PygameDisplay(self.config)
        self.display.init()

        zm_client = get_zoneminder_client(self.config)
        group_tracker = RefreshingZmGroupTracker(zm_client)
        zm_stream_component = ZoneminderStreamComponent(self.config, self.event_bus, zm_client, group_tracker)
        group_selector_component = GroupSelectorComponent(self.config, self.event_bus, group_tracker)
        monitor_selector_component = MonitorSelectorComponent(self.config, self.event_bus, group_tracker)
        shutdown_prompt_component = ShutdownPromptSelector(self.config, self.event_bus)
        self.component_manager = AppComponentManager(self.display, self.event_bus, zm_stream_component,
                                                     [group_selector_component, monitor_selector_component,
                                                      shutdown_prompt_component])
        self.app_controller = AppController(self.event_bus)

        self.input_handlers = get_input_handlers(self.event_bus, self.config)

    def run(self):
        while True:
            self.component_manager.update()
            for handler in self.input_handlers:
                handler.check_input_commands()
            time.sleep(.1)


if __name__ == '__main__':
    app = ZmApplet()
    app.run()
