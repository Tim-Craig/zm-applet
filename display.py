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
        self.display_info = None
        self.background = None
        self.mjpeg_streamer = None

    def init(self):
        pygame.init()
        self.display_info = pygame.display.Info()
        self.display = pygame.display.set_mode((self.display_info.current_w, self.display_info.current_h),
                                               pygame.FULLSCREEN)
        self.background = pygame.Surface((self.display_info.current_w, self.display_info.current_h))
        self.background.fill(pygame.Color('#E8E8E8'))
        self.display.blit(self.background, (0,0))

    def set_stream(self, mjpeg_streamer):
        self.mjpeg_streamer = mjpeg_streamer

    def update(self):
        image = self.mjpeg_streamer.next_frame()
        image_panel = pygame.image.load(image).convert()
        image_panel = pygame.transform.scale(image_panel, (self.display_info.current_w, self.display_info.current_h))
        self.display.blit(image_panel, (0,0))
        pygame.display.update()


if __name__ == "__main__":
    from zoneminder.client import ZoneMinderClient
    from mjpeg_streamer import MjpegStreamer
    import time
    display = PygameDisplay()
    display.init()

    client = ZoneMinderClient('localhost', 8080, 'zm')
    stream = client.get_monitor_stream("1")
    display.set_stream(MjpegStreamer(stream))
    for i in xrange(20):
        display.update()
        time.sleep(.1)

    import sys

    sys.exit(0)