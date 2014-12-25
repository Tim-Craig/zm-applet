import pygame
from display import PygameDisplay
from zoneminder.client import ZoneMinderClient
from zoneminder.group_tracker import ZmGroupTracker
from controller import AppController
from input_handler import PygameInputHandler

import sys
import time

class ZmApplet(object):
    def __init__(self):
        def get_input_handlers(controller):
            handlers = [PygameInputHandler(controller)]
            try:
                from pi_input_handler import PiInputHandler
                handlers.append(PiInputHandler(controller))
            except ImportError:
                print('Unable to import raspberrypi input handler')
            return handlers

        self.display = PygameDisplay()
        self.display.init()
        self.zm_client = ZoneMinderClient('overlord', 80, 'zm')
        self.group_tracker = ZmGroupTracker(self.zm_client.get_xml_console())
        self.controller = AppController(self.display, self.group_tracker, self.zm_client)
        self.input_handlers = get_input_handlers(self.controller)

        self.controller.start()

    def run(self):

        while True:
            for handler in self.input_handlers:
                handler.check_input_commands()
            self.controller.update()
            time.sleep(.01)


if __name__ == '__main__':
    app = ZmApplet()
    app.run()
