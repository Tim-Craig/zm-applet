import pygame


class display(object):
    def init(self):
        pass
    def run_stream(self):
        pass

class pygameDisplay(display):
    def __init__(self):
        self.display = None

    def init(self):
        pygame.init()
        display_info = pygame.display.Info()
        self.display = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        self.display.fill((0,0,0))

if __name__ == "__main__":
    display = pygameDisplay()
    display.init()
    import time
    time.sleep(2)
    import sys
    sys.exit(0)