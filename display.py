import pygame


class PygameDisplay(object):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.display = None
        self.view = None

    def init(self):
        pygame.init()
        display_info = pygame.display.Info()
        self.display = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        #self.display = pygame.display.set_mode((320, 200))
        pygame.mouse.set_visible(False)
        if self.view:
            self.view.start_view(self.get_display_size())

    def get_display_size(self):
        size = None
        if self.display:
            size = self.display.get_size()
        return size

    def set_view(self, view):
        self.view = view
        self.view.start_view(self.get_display_size())

    def update(self):
        if self.display:
            self.view.paint(self.display)
            pygame.display.update()