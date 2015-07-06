import types
import app_events

def get_config():
    def get_defaults():
        return {'server_host': 'overlord',
                'server_port': '80',
                'zm_web_path': 'zm',
                'user_name': None,
                'password': None,
                'zms_web_path': 'cgi-bin/zms',
                'quit': 'escape',
                'prev_monitor': ('left', 'GPIO_23'),
                'next_monitor': ('right', 'GPIO_22'),
                'shutdown': 'GPIO_27+GPIO_18'
                }

    return get_defaults()


class AppConfig(object):
    def __init__(self):
        self.config = get_config()

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
        for config_name in app_events.get_event_type_configs():
            if config_name in self.config.keys():
                config_value = self.config[config_name]
                matched_values = find_matching_values(config_value, event_config_values)
                if matched_values:
                    matching_config_map[config_name] = matched_values
        return matching_config_map