from collections import namedtuple

import mock
from mock import patch
from pygame.locals import *

from input_handler import PygameInputHandler
from app_config import AppConfig
from controller import AppController
from app_events import *

Event = namedtuple('Event', ['type', 'key'])


@patch('input_handler.pygame.event')
def test_pygame_input_handler(pygame_event):
    pygame_event.get.return_value = [Event(KEYDOWN, K_ESCAPE)]
    controller_mock = mock.create_autospec(AppController)
    input_handler = PygameInputHandler(controller_mock, AppConfig())
    input_handler.check_input_commands(0.1)
    controller_mock.process_event.assert_called_once_with(EVENT_QUIT)


@patch('input_handler.pygame.event')
def test_pygame_input_handler(pygame_event):
    pygame_event.get.return_value = [Event(KEYDOWN, K_LEFT)]
    controller_mock = mock.create_autospec(AppController)
    input_handler = PygameInputHandler(controller_mock, AppConfig())
    input_handler.check_input_commands(0.1)
    controller_mock.process_event.assert_called_once_with(EVENT_PREV_MONITOR)


@patch('input_handler.pygame.event')
def test_pygame_input_handler(pygame_event):
    pygame_event.get.return_value = [Event(KEYDOWN, K_RIGHT)]
    controller_mock = mock.create_autospec(AppController)
    input_handler = PygameInputHandler(controller_mock, AppConfig())
    input_handler.check_input_commands(0.1)
    controller_mock.process_event.assert_called_once_with(EVENT_NEXT_MONITOR)
