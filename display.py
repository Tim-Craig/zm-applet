import pygame
from app_config import *


class PygameDisplay(object):
    def __init__(self, app_config, mouse_visible=False):
        super(self.__class__, self).__init__()
        self.display = None
        self.view = None
        self.overlay = None
        self.mouse_visible = mouse_visible
        self.app_config = app_config

    def init(self):
        def get_desired_screen_size():
            size = None
            if self.app_config.config[SCREEN_SIZE] == SCREEN_SIZE_VALUE_FULLSCREEN or \
                            self.app_config.config[WINDOW_MODE] == WINDOW_MODE_VALUE_FULLSCREEN:
                display_info = pygame.display.Info()
                size = (display_info.current_w, display_info.current_h)
            else:
                size_setting = self.app_config.config[SCREEN_SIZE].split('x')
                size = (int(size_setting[0]), int(size_setting[1]))
            return size

        def get_screen_mode_flags():
            mode_flags = None
            window_mode = self.app_config.config[WINDOW_MODE]
            if window_mode == WINDOW_MODE_VALUE_BORDERLESS:
                mode_flags = pygame.NOFRAME
            elif window_mode == WINDOW_MODE_VALUE_FULLSCREEN:
                mode_flags = pygame.FULLSCREEN
            return mode_flags

        pygame.init()
        screen_size = get_desired_screen_size()
        flags = get_screen_mode_flags()
        if flags:
            self.display = pygame.display.set_mode(screen_size, flags)
        else:
            self.display = pygame.display.set_mode(screen_size)
        pygame.mouse.set_visible(self.mouse_visible)
        if self.view:
            self.view.start_view(self.get_display_size())

    def get_display_size(self):
        size = None
        if self.display:
            size = self.display.get_size()
        return size

    def set_view(self, view):
        if self.view:
            self.view.close()
        self.view = view
        self.view.start_view(self.get_display_size())

    def set_overlay(self, overlay):
        if self.overlay:
            self.overlay.close()
        self.overlay = overlay
        if self.overlay:
            self.overlay.start_view(self.get_display_size())

    def update(self):
        if self.display:
            self.view.paint(self.display)
            if self.overlay:
                self.overlay.paint(self.display)
            pygame.display.update()
