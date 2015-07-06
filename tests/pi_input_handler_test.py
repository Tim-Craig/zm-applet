import mock
from mock import patch
from pi_input_handler import PiInputHandler, GPIO_23, GPIO_22, GPIO_27, GPIO_18
from app_config import AppConfig
from app_events import *
from controller import AppController


@patch('pi_input_handler.GPIO')
def test_pygame_input_handler_default_action_for_gpio_23(gpio_mock):
    controller_mock = mock.create_autospec(AppController)
    input_handler = PiInputHandler(controller_mock, AppConfig())
    input_handler.gpio_events = {GPIO_23}
    input_handler.check_input_commands(0.1)
    controller_mock.process_event.assert_called_once_with(EVENT_PREV_MONITOR)

@patch('pi_input_handler.GPIO')
def test_pygame_input_handler_default_action_for_gpio_22(gpio_mock):
    controller_mock = mock.create_autospec(AppController)
    input_handler = PiInputHandler(controller_mock, AppConfig())
    input_handler.gpio_events = {GPIO_22}
    input_handler.check_input_commands(0.1)
    controller_mock.process_event.assert_called_once_with(EVENT_NEXT_MONITOR)

@patch('pi_input_handler.GPIO')
def test_pygame_input_handler_default_action_for_gpio_27_plus_18(gpio_mock):
    controller_mock = mock.create_autospec(AppController)
    input_handler = PiInputHandler(controller_mock, AppConfig())
    input_handler.gpio_events = {GPIO_27, GPIO_18}
    input_handler.check_input_commands(0.1)
    controller_mock.process_event.assert_called_once_with(EVENT_SHUTDOWN)
