from app_config import *


def test_get_event_configs_assigned_to_input_labels_for_gpio():
    app_config = AppConfig()
    supported_values = ['GPIO_23', 'GPIO_22', 'GPIO_27', 'GPIO_18']
    config_values = app_config.get_event_configs_assigned_to_input_labels(supported_values)
    assert (config_values[PREV_MONITOR][0] == 'GPIO_23')
    assert (config_values[NEXT_MONITOR][0] == 'GPIO_22')
    assert (config_values[SHUTDOWN][0] == ['GPIO_27', 'GPIO_18'])


def test_get_event_configs_assigned_to_input_labels_for_key_events():
    app_config = AppConfig()
    supported_values = ['left', 'right', 'escape']
    config_values = app_config.get_event_configs_assigned_to_input_labels(supported_values)
    assert (config_values[PREV_MONITOR][0] == 'left')
    assert (config_values[NEXT_MONITOR][0] == 'right')
    assert (config_values[QUIT][0] == 'escape')
