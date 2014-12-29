import pygame


class Display(object):
    def init(self):
        pass

    def set_stream(self, mjpeg_streamer):
        pass

    def update(self):
        pass


class PygameDisplay(Display):
    def __init__(self):
        self.display = None
        self.display_size = None
        self.background = None
        self.mjpeg_streamer = None

    def init(self):
        pygame.init()
        display_info = pygame.display.Info()
        self.display = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        self.background = pygame.Surface(self.display.get_size())
        self.background.fill(pygame.Color('#E8E8E8'))
        self.display.blit(self.background, (0, 0))
        pygame.mouse.set_visible(False)

    def get_display_size(self):
        size = None
        if self.display:
            size = self.display.get_size()
        return size

    def set_stream(self, mjpeg_streamer):
        self.mjpeg_streamer = mjpeg_streamer

    def update(self):
        image = self.mjpeg_streamer.next_frame()
        image_panel = pygame.image.load(image).convert()
        image_panel = pygame.transform.scale(image_panel, self.display.get_size())
        self.display.blit(image_panel, (0, 0))
        pygame.display.update()