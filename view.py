import pygame
import pygame.draw
import threading
from Queue import Queue
import time
from image_streamer import MessageStreamer
from zoneminder.zoneminder_monitor_streamer import ZoneminderMonitorStreamer

def get_scale(monitor, display_size):
    x_scale = float(display_size[0]) / float(monitor.width)
    y_scale = float(display_size[1]) / float(monitor.height)
    scale = int(x_scale * 100) if x_scale < y_scale else int(y_scale * 100)
    return scale if scale < 100 else 100


class View(object):
    def __init__(self):
        self.position = None
        self.size = None

    def start_view(self, size, position=(0, 0)):
        self.position = position
        self.size = size

    def paint(self, display):
        pass

    def close(self):
        pass


class StreamerView(View):
    def __init__(self):
        super(StreamerView, self).__init__()
        self.stream_panel = None

    def start_view(self, size, position=(0, 0)):
        super(StreamerView, self).start_view(size, position)
        self.stream_panel = ThreadedStreamLoader(size)
        self.stream_panel.start()

    def set_stream(self, image_streamer):
        self.stream_panel.set_streamer(image_streamer)

    def get_rect(self):
        return self.position[0], self.position[1], self.size[0], self.size[1]

    def paint(self, display):
        if self.stream_panel.image:
            display.blit(self.stream_panel.image, (0, 0))
        else:
            pygame.draw.rect(display, (0, 0, 200), self.get_rect())

    def close(self):
        self.sream_panel.close()


class ThreadedStreamLoader(threading.Thread):
    def __init__(self, size):
        super(ThreadedStreamLoader, self).__init__()
        self._streamer = None
        self.size = size
        self.image = None
        self.new_stream_queue = Queue()
        self.daemon = True
        self.is_running = True

    def set_streamer(self, mjpeg_streamer):
        self.new_stream_queue.put(mjpeg_streamer)

    def run(self):
        def load_next_image():
            original_image = self._streamer.next_frame()
            if original_image.get_size() == self.size:
                self.image = original_image
            else:
                self.image = pygame.transform.scale(original_image, self.size)

        def switch_stream():
            self._streamer = self.new_stream_queue.get()
                # flush out other streams
            while not self.new_stream_queue.empty():
                self.new_stream_queue.get()
                self.new_stream_queue.task_done()

        while self.is_running:
            if self._streamer:
                load_next_image()
            if not self.new_stream_queue.empty():
                switch_stream()
        time.sleep(.5)

    def close(self):
        self.is_running = False


class ZoneminderStreamView(StreamerView):
    def __init__(self, zm_client, group_tracker):
        super(ZoneminderStreamView, self).__init__()
        self.zm_client = zm_client
        self.group_tracker = group_tracker
        self.cur_monitor = group_tracker.get_current_monitor()

    def start_view(self, size, position=(0, 0)):
        super(ZoneminderStreamView, self).start_view(size, position)
        self.start_stream(self.cur_monitor)

    def start_stream(self, monitor):
        self.cur_monitor = monitor
        streamer = None
        if monitor:
            scale = get_scale(monitor, self.size)
            streamer = ZoneminderMonitorStreamer(self.zm_client, monitor.id, scale, self.size)
        else:
            streamer = MessageStreamer(self.size, 'Unable to get monitor stream.  Retrying...')
            retry_runner = threading.Thread(target=self._refresh)
            retry_runner.daemon = True
            retry_runner.start()
        self.set_stream(streamer)

    def _refresh(self):
       time.sleep(3)
       self.start_stream(self.group_tracker.get_current_monitor())

class ListView(View):
    def __init__(self):
        self.position = None
        self.size = None

    def paint(self, display):
        pass

    def close(self):
        pass
