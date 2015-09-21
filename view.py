import pygame
from pygame import Surface
import pygame.draw
import threading
from Queue import Queue
import time
from image_streamer import MessageStreamer
from zoneminder.zoneminder_monitor_streamer import ZoneminderMonitorStreamer

TEXT_ALIGNMENT_LEFT = "left"
TEXT_ALIGNMENT_CENTER = "center"


def get_scale(monitor, display_size):
    x_scale = float(display_size[0]) / float(monitor.width)
    y_scale = float(display_size[1]) / float(monitor.height)
    scale = int(x_scale * 100) if x_scale < y_scale else int(y_scale * 100)
    return scale if scale < 100 else 100


class View(object):
    def __init__(self):
        self.size = None

    def start_view(self, size):
        self.size = size

    def paint(self, display):
        pass

    def close(self):
        pass


class StreamerView(View):
    def __init__(self):
        super(StreamerView, self).__init__()
        self.stream_panel = None

    def start_view(self, size, ):
        super(StreamerView, self).start_view(size)
        self.stream_panel = ThreadedStreamLoader(size)
        self.stream_panel.start()

    def set_stream(self, image_streamer):
        self.stream_panel.set_streamer(image_streamer)

    def get_rect(self):
        return 0, 1, self.size[0], self.size[1]

    def paint(self, display):
        if self.stream_panel.image:
            display.blit(self.stream_panel.image, (0, 0))
        else:
            pygame.draw.rect(display, (0, 0, 200), self.get_rect())

    def close(self):
        self.stream_panel.close()


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
        self.cur_monitor = None

    def start_view(self, size):
        super(ZoneminderStreamView, self).start_view(size)
        self.cur_monitor = self.group_tracker.get_current_monitor()
        self.start_stream(self.cur_monitor)

    def start_stream(self, monitor):
        self.cur_monitor = monitor
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
    def __init__(self, caption, item_list, caption_gb_color=(200, 60, 180), bg_color=(0, 0, 180),
                 font_color=(255, 255, 255), border_color=(128, 128, 128)):
        super(ListView, self).__init__()
        self.caption = caption
        self.caption_height = None
        self.item_list = item_list
        self.caption_bg_color = caption_gb_color
        self.bg_color = bg_color
        self.font_color = font_color
        self.caption_image = None
        self.item_position_tracker = None
        self.list_image = None
        self.list_image_height = None
        self.scroll_length = 0
        self.scroll_pos = 0
        self.border_color = border_color

    def start_view(self, size):
        super(ListView, self).start_view(size)
        self.load_view_list()

    def load_view_list(self):
        def build_text_image(text, img_gb_color=self.bg_color, font_size=30, alignment=TEXT_ALIGNMENT_LEFT, verticle_margins=10, border_color=self.border_color):
            font = pygame.font.SysFont("monospace", font_size)
            text_img = font.render(text, True, self.font_color)
            text_size = text_img.get_size()
            centered_text_img_height = text_size[1] + (verticle_margins * 2)
            centered_text_img = Surface((self.size[0], centered_text_img_height))
            text_pos_x = 0
            if alignment == TEXT_ALIGNMENT_CENTER:
                text_pos_x = (self.size[0] / 2) - (text_size[0] / 2)
            text_pos_y = (centered_text_img_height / 2) - (text_size[1] / 2)
            centered_text_img.fill(img_gb_color)
            if border_color:
                pygame.draw.rect(centered_text_img, border_color, [0, 0, self.size[0], centered_text_img_height], 1)
            centered_text_img.blit(text_img, (text_pos_x, text_pos_y))
            return centered_text_img

        def build_list_structures(panel_size):
            item_text_imgs = []
            position_tracker = _ItemPositionTracker()
            list_height = 0
            for item in self.item_list:
                item_img = build_text_image(item)
                item_text_imgs.append(item_img)
                list_height += item_img.get_size()[1]
                position_tracker.add_item(item, item_img.get_size()[1])
            return combine_imgs(item_text_imgs, (panel_size[0], position_tracker.current_height)), position_tracker

        def combine_imgs(img_list, list_size):
            combined_img = Surface((list_size[0], list_size[1]))
            y = 0
            for img in img_list:
                combined_img.blit(img, (0, y))
                y += img.get_size()[1]
            return combined_img

        self.caption_image = build_text_image(self.caption, self.caption_bg_color, 35, TEXT_ALIGNMENT_CENTER, 0, None)
        self.caption_height = self.caption_image.get_size()[1]
        self.list_image, self.item_position_tracker = build_list_structures(self.size)
        self.scroll_length = self.list_image.get_size()[1] - (self.size[1] - self.caption_height)

    def drag(self, drag_start_point, delta):
        if self.caption_height <= drag_start_point[1] <= self.size[1]:
            self.scroll_pos -= delta[1]
            if self.scroll_pos < 0:
                self.scroll_pos = 0
            elif self.scroll_pos > self.scroll_length:
                self.scroll_pos = self.scroll_length

    def process_click(self, data):
        y_pos = data[1]
        selection = None
        if y_pos >= self.caption_height:
            selection = self.item_position_tracker.get_item(data[1] - self.caption_height + self.scroll_pos)
        return selection

    def paint(self, display):
        def check_and_fill_uncovered_area():
            list_image_size = self.list_image.get_size()
            display_size = display.get_size()
            covered_height = (caption_height + list_image_size[1])
            uncovered_height = display_size[1] - covered_height
            if uncovered_height > 0:
                width = display_size[0]
                pygame.draw.rect(display, self.bg_color, (0,covered_height,width,uncovered_height))
        caption_height = self.caption_image.get_size()[1]
        display.blit(self.list_image, (0, caption_height - self.scroll_pos))
        display.blit(self.caption_image, (0, 0))
        check_and_fill_uncovered_area()

    def close(self):
        pass


class _ItemPositionTracker(object):
    def __init__(self):
        self.current_height = 0
        self.item_ranges = []

    def add_item(self, item, height):
        self.item_ranges.append((item, (self.current_height, self.current_height + height)))
        self.current_height += height

    def get_item(self, y_pos):
        for item in self.item_ranges:
            if y_pos < item[1][1]:
                return item[0]
        return None
