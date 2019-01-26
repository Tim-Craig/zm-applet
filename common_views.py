from datetime import datetime

import pygame
from pygame import Surface

from util import create_message_image
from view import View

TEXT_ALIGNMENT_LEFT = "left"
TEXT_ALIGNMENT_CENTER = "center"


class MessageView(View):
    def __init__(self, message, background_color=(0, 0, 200), font_color=(255, 255, 255)):
        super(MessageView, self).__init__()
        self.message = message
        self.image = None
        self.background_color = background_color
        self.font_color = font_color

    def set_message(self, message):
        self.message = message
        # if the size has been set, then the view had already been started and we'll need to build a new image
        if self.size:
            self.image = create_message_image(message=self.message, image_size=self.size, font_color=self.font_color,
                                              bg_color=self.background_color)
            self.need_repaint = True

    def start_view(self, size):
        super(MessageView, self).start_view(size)
        self.image = create_message_image(message=self.message, image_size=size, font_color=self.font_color,
                                          bg_color=self.background_color)
        self.need_repaint = True

    def paint(self, pos, display):
        super(MessageView, self).paint(pos, display)
        if self.image:
            display.blit(self.image, pos)


class ImageView(View):
    def __init__(self):
        super(ImageView, self).__init__()
        self.image = None

    def set_image(self, image):
        self.image = image
        if image.get_rect().size != self.size:
            self.image = pygame.transform.scale(image, self.size)
        self.need_repaint = True

    def paint(self, pos, display):
        super(ImageView, self).paint(pos, display)
        if self.image:
            display.blit(self.image, pos)
        else:
            pygame.draw.rect(display, (pos[0], pos[1], 200), (pos[0], pos[1], self.size[0], self.size[1]))


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
        if self.item_list:
            self.load_view_list()
        self.need_repaint = True

    def set_item_list(self, item_list):
        self.item_list = item_list
        if self.item_list:
            self.load_view_list()
        self.need_repaint = True

    def load_view_list(self):
        def build_text_image(text, img_gb_color=self.bg_color, font_size=30, alignment=TEXT_ALIGNMENT_LEFT,
                             verticle_margins=10, border_color=self.border_color):
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

    def drag(self, drag_start_point, current_pos, delta):
        if self.caption_height <= drag_start_point[1] <= self.size[1]:
            self.scroll_pos -= delta[1]
            if self.scroll_pos < 0:
                self.scroll_pos = 0
            elif self.scroll_pos > self.scroll_length:
                self.scroll_pos = self.scroll_length
        self.need_repaint = True

    def process_click(self, data):
        y_pos = data[1]
        selection = None
        if y_pos >= self.caption_height:
            selection = self.item_position_tracker.get_item(data[1] - self.caption_height + self.scroll_pos)
        return selection

    def paint(self, pos, display):
        def check_and_fill_uncovered_area():
            list_image_size = self.list_image.get_size()
            covered_height = (caption_height + list_image_size[1])
            uncovered_height = self.size[1] - covered_height
            if uncovered_height > 0:
                width = self.size[0]
                pygame.draw.rect(display, self.bg_color, (pos[0], pos[1] + covered_height, width, uncovered_height))

        super(ListView, self).paint(pos, display)
        caption_height = self.caption_image.get_size()[1]
        display.blit(self.list_image, (pos[0], pos[1] + caption_height - self.scroll_pos))
        display.blit(self.caption_image, pos)
        check_and_fill_uncovered_area()


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


class Button(View):
    BUTTON_SLEEP_TIME = 250
    INNER_RECT_SIZE_OFFSET = 3

    def __init__(self, label, action=None):
        super(Button, self).__init__()
        self.action = action
        self._label = label
        self._label_img = None
        self._is_pressed = False
        self._sleep_time = 0
        self._inner_rect = (0, 0, 0, 0)

    def start_view(self, size):
        super(Button, self).start_view(size)
        offset = Button.INNER_RECT_SIZE_OFFSET
        self._inner_rect = (offset, offset, size[0] - (offset * 2), size[1] - (offset * 2))
        self._label_img = create_message_image(self._label, (self._inner_rect[2], self._inner_rect[3]),
                                               bg_color=(0, 0, 0, 0))

    DARKER_COLOR = (77, 133, 255)
    LIGHTER_COLOR = (179, 203, 255)

    def paint(self, pos, display):
        super(Button, self).paint(pos, display)
        if self._is_pressed or self._sleep_time > 0:
            pygame.draw.rect(display, Button.DARKER_COLOR, (pos[0], pos[1], self.size[0], self.size[1]))
        else:
            pygame.draw.rect(display, Button.LIGHTER_COLOR, (pos[0], pos[1], self.size[0], self.size[1]))
        inner_rect = (
            self._inner_rect[0] + pos[0], self._inner_rect[1] + pos[1], self._inner_rect[2], self._inner_rect[3])
        pygame.draw.rect(display, Button.DARKER_COLOR, inner_rect)
        display.blit(self._label_img, (inner_rect[0], inner_rect[1]))

    def process_pressed(self, pos):
        super(Button, self).process_pressed(pos)
        if self._sleep_time <= 0:
            if 0 <= pos[0] <= self.size[0] and 0 <= pos[1] <= self.size[1]:
                self._is_pressed = True
                self.need_repaint = True

    def process_press_released(self, pos):
        super(Button, self).process_press_released(pos)
        if self._sleep_time <= 0:
            if self._is_pressed:
                self._is_pressed = True
                self.need_repaint = True
                self._sleep_time = self.BUTTON_SLEEP_TIME
                self.action()

    def drag(self, drag_start_point, current_pos, delta):
        super(Button, self).drag(drag_start_point, current_pos, delta)
        if self._is_pressed:
            if current_pos[0] < 0 or current_pos[0] > self.size[0] or \
                    current_pos[1] < 0 or current_pos[1] > self.size[1]:
                self._is_pressed = False
                self.need_repaint = True
        elif 0 <= drag_start_point[0] <= self.size[0] and 0 <= drag_start_point[1] <= self.size[1]:
            if 0 <= current_pos[0] <= self.size[0] and 0 <= current_pos[1] <= self.size[1]:
                self._is_pressed = True
                self.need_repaint = True

    def update(self, time_elapsed):
        if self._sleep_time > 0:
            self._sleep_time -= time_elapsed
            if self._sleep_time <= 0:
                self._sleep_time = 0
                self._is_pressed = False
                self.need_repaint = True


class ArrowDisplay(View):
    ARROW_EDGE_MARGIN = 3

    LEFT_ARROW = 0
    RIGHT_ARROW = 1

    def __init__(self, arrow_direction, click_callback=None, color=(0, 255, 0)):
        super(ArrowDisplay, self).__init__()
        self._arrow_direction = arrow_direction
        self._click_callback = click_callback
        self._color = color
        self._arrow = None
        self._last_position = None
        self._translated_arrow = None
        self._show_arrow = False

    def show_arrow(self):
        self.need_repaint = True
        self._show_arrow = True

    def hide_arrow(self):
        self.need_repaint = True
        self._show_arrow = False

    def start_view(self, size):
        def round_int(num):
            return int(round(num) - .5) + (num > 0)

        def build_arrow():
            arrow_half_height = round_int(size[1] / 2)
            arrow_width = arrow_half_height * 2
            center_y = int(size[1] / 2)

            self._arrow = []
            if self._arrow_direction == ArrowDisplay.LEFT_ARROW:
                x = self.ARROW_EDGE_MARGIN
                y = center_y
                self._arrow.append((x, y))
                x = self.ARROW_EDGE_MARGIN + arrow_width
                y = center_y - arrow_half_height
                self._arrow.append((x, y))
                x = self.ARROW_EDGE_MARGIN + arrow_width
                y = center_y + arrow_half_height
                self._arrow.append((x, y))
            else:  # RIGHT_ARROW
                x = size[0] - self.ARROW_EDGE_MARGIN
                y = center_y
                self._arrow.append((x, y))
                x = size[0] - self.ARROW_EDGE_MARGIN - arrow_width
                y = center_y - arrow_half_height
                self._arrow.append((x, y))
                x = size[0] - self.ARROW_EDGE_MARGIN - arrow_width
                y = center_y + arrow_half_height
                self._arrow.append((x, y))

        super(ArrowDisplay, self).start_view(size)
        build_arrow()

    def process_click(self, pos):
        if self._click_callback:
            self._click_callback()

    def paint(self, pos, display):
        super(ArrowDisplay, self).paint(pos, display)
        if pos != self._last_position:
            self._last_position = pos
            self._translated_arrow = [(point[0] + pos[0], point[1] + pos[1]) for point in self._arrow]
        if self._show_arrow:
            pygame.draw.polygon(display, self._color, self._translated_arrow)


class CurrentTimeLabel(MessageView):
    BACKGROUND_COLOR = (255, 255, 255)
    FONT_COLOR = (0, 0, 0)

    def __init__(self):
        self.minute = datetime.today().minute
        super(CurrentTimeLabel, self).__init__(self._get_time_str(), CurrentTimeLabel.FONT_COLOR,
                                               CurrentTimeLabel.BACKGROUND_COLOR)

    def update(self, time_elapsed):
        current_minute = datetime.today().minute
        if self.minute != current_minute:
            self.minute = current_minute
            self.set_message(self._get_time_str())

    @staticmethod
    def _get_time_str():
        return datetime.today().strftime("%m/%d/%y %I:%M %p")
