from app_config import AppConfig


def test_get_event_configs_assigned_to_input_labels_for_gpio():
    app_config = AppConfig()
    supported_values = ['GPIO_23', 'GPIO_22', 'GPIO_27', 'GPIO_18']
    config_values = app_config.get_event_configs_assigned_to_input_labels(supported_values)
    assert(config_values['prev_monitor'][0] == 'GPIO_23')
    assert(config_values['next_monitor'][0] == 'GPIO_22')
    assert(config_values['shutdown'][0] == ['GPIO_27', 'GPIO_18'])


def test_get_event_configs_assigned_to_input_labels_for_key_events():
    app_config = AppConfig()
    supported_values = ['left', 'right', 'escape']
    config_values = app_config.get_event_configs_assigned_to_input_labels(supported_values)
    assert(config_values['prev_monitor'][0] == 'left')
    assert(config_values['next_monitor'][0] == 'right')
    assert(config_values['quit'][0] == 'escape')