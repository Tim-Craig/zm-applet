import ConfigParser
import json
import types
from os.path import expanduser

import app_events

SERVER_HOST = 'server_host'
SERVER_PORT = 'server_port'
ZM_WEB_PATH = 'zm_web_path'
USER_NAME = 'user_name'
SHUTDOWN_PROMPT = 'shutdown_prompt'
PASSWORD = 'password'
ZMS_WEB_PATH = 'zms_web_path'
QUIT = 'quit'
PREV_MONITOR = 'prev_monitor'
NEXT_MONITOR = 'next_monitor'
OPEN_GROUP_VIEW = 'open_group_view'
OPEN_MENU = 'open_menu'
SHUTDOWN = 'shutdown'
# windowed, borderless, or fullscreen
WINDOW_MODE = 'window_mode'
WINDOW_MODE_VALUE_WINDOWED = 'windowed'
WINDOW_MODE_VALUE_BORDERLESS = 'borderless'
WINDOW_MODE_VALUE_FULLSCREEN = 'fullscreen'
# either <width>x<height> (e.g. 320x240) or 'full' for full size of display, this is ignored if window_mode is full
# screen
SCREEN_SIZE = 'screen_size'
SCREEN_SIZE_VALUE_FULLSCREEN = 'full'
STARTING_GROUP_NAME = 'starting_group_name'
STARTING_MONITOR_NAME = 'starting_monitor_name'
CYCLE_MODE = 'cycle_mode'


def get_config():
    def get_defaults():
        return {SERVER_HOST: 'localhost',
                SERVER_PORT: '8080',
                ZM_WEB_PATH: 'zm',
                USER_NAME: None,
                PASSWORD: None,
                ZMS_WEB_PATH: 'cgi-bin/zms',
                QUIT: 'escape',
                PREV_MONITOR: '["left","GPIO_23"]',
                NEXT_MONITOR: '["right", "GPIO_22"]',
                OPEN_GROUP_VIEW: '["space", "GPIO_27"]',
                OPEN_MENU: 'GPIO_18',
                SHUTDOWN: 'GPIO_27+GPIO_18',
                WINDOW_MODE: 'borderless',
                SCREEN_SIZE: 'full',
                STARTING_GROUP_NAME: None,
                STARTING_MONITOR_NAME: None
                }

    config = ConfigParser.SafeConfigParser(get_defaults())
    config.read(['zm_applet.cfg', expanduser('~/.zm_applet.cfg')])
    return config


class AppConfig(object):
    def __init__(self):
        self.config = dict(get_config().items('DEFAULT'))
        for name, value in self.config.iteritems():
            if value.strip().startswith('['):
                self.config[name] = json.loads(value.strip())

    def get_event_configs_assigned_to_input_labels(self, event_config_values):
        def set_in_set(set1, set2):
            for item in set1:
                if item not in set2:
                    return False
            return True

        def find_matching_string_value(value_to_find, list_of_values):
            return_val = None
            if '+' in value_to_find:
                values = value_to_find.split('+')
                if set_in_set(values, list_of_values):
                    return_val = values
            else:
                return_val = value_to_find if value_to_find in list_of_values else None
            return return_val

        def find_matching_values(target_value, possible_values):
            matches = []
            if isinstance(target_value, types.StringTypes):
                match = find_matching_string_value(target_value, possible_values)
                if match:
                    matches.append(match)
            else:
                for value in target_value:
                    match = find_matching_string_value(value, possible_values)
                    if match:
                        matches.append(match)
            return matches if len(matches) > 0 else None

        matching_config_map = {}
        for config_name in app_events.CONFIG_EVENT_TYPES:
            if config_name in self.config.keys():
                config_value = self.config[config_name]
                matched_values = find_matching_values(config_value, event_config_values)
                if matched_values:
                    matching_config_map[config_name] = matched_values
        return matching_config_map
