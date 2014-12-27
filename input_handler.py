import pygame
from pygame.locals import *
import sys


class InputHandler(object):
    def __init__(self, controller):
        self.controller = controller

    def check_input_commands(self, elapsed_time):
        pass


class PygameInputHandler(InputHandler):
    def check_input_commands(self, elapsed_time):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                elif event.key == K_LEFT:
                    self.controller.move_to_prev_monitor_stream()
                elif event.key == K_RIGHT:
                    self.controller.move_to_next_monitor_stream()