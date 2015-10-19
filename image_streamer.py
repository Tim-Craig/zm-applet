import StringIO
import time

from pygame import Surface
import pygame


class ImageStreamer(object):
    def next_frame(self):
        pass


class MessageStreamer(ImageStreamer):
    def __init__(self, size, message):
        self.surface = Surface(size)
        self.surface.fill((0, 0, 200))
        font = pygame.font.SysFont("monospace", 12)
        render_txt = font.render(message, True, (255, 255, 255))
        msg_size = render_txt.get_size()
        x = (size[0] / 2) - (msg_size[0] / 2)
        y = (size[1] / 2) - (msg_size[1] / 2)
        self.surface.blit(render_txt, (x, y))

    def next_frame(self):
        return self.surface


class MjpegStreamer(ImageStreamer):
    def __init__(self, stream=None):
        self.stream = None
        self.set_stream(stream)

    def set_stream(self, stream):
        if self.stream:
            self.stream.close()
        self.stream = stream

    def next_frame(self):
        def read_line():
            content = None
            try:
                content = self.stream.readline()
            except Exception:
                raise DeadConnectionException
            return content

        if not self.stream:
            return None

        dead_connection_watch_dog = DeadConnectionWatchDog()
        content_length_line = read_line()
        while content_length_line[0:15] != 'Content-Length:':
            content_length_line = read_line()
            dead_connection_watch_dog.check(content_length_line)
        count = int(content_length_line[16:])
        try:
            img_buffer = self.stream.read(count)
        except Exception:
            raise DeadConnectionException()
        while len(img_buffer) != 0 and img_buffer[0] != chr(0xff):
            img_buffer = img_buffer[1:]

        image_data = StringIO.StringIO(img_buffer)
        return pygame.image.load(image_data).convert()


class DeadConnectionWatchDog(object):
    def __init__(self, dead_wait_time=10):
        self.dead_wait_time = dead_wait_time
        self.current_dead_wait = 0
        self.last_time = 0

    def check(self, line_read):
        if self.last_time == 0:
            self.last_time = time.time()
        if len(line_read) == 0:
            self.current_dead_wait += time.time() - self.last_time
            if self.current_dead_wait > self.dead_wait_time:
                raise DeadConnectionException()
        else:
            self.current_dead_wait = 0
        self.last_time = time.time()


class DeadConnectionException(Exception):
    pass
