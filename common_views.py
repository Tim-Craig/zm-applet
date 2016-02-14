import pygame
from pygame import Surface

from util import create_message_image
from view import View

TEXT_ALIGNMENT_LEFT = "left"
TEXT_ALIGNMENT_CENTER = "center"


class MessageView(View):
    def __init__(self, message):
        super(MessageView, self).__init__()
        self.message = message
        self.image = None

    def set_message(self, message):
        self.message = message
        # if the size has been set, then the view had already been started and we'll need to build a new image
        if self.size:
            self.image = create_message_image(self.message, self.size)
            self.need_repaint = True

    def start_view(self, size):
        super(MessageView, self).start_view(size)
        self.image = create_message_image(self.message, size)
        self.need_repaint = True

    def get_rect(self):
        return 0, 1, self.size[0], self.size[1]

    def paint(self, display):
        if self.image:
            display.blit(self.image, (0, 0))


class ImageView(View):
    def __init__(self):
        super(ImageView, self).__init__()
        self.image = None

    def set_image(self, image):
        self.image = image
        if image.get_rect().size != self.size:
            self.image = pygame.transform.scale(image, self.size)
        self.need_repaint = True

    def get_rect(self):
        return 0, 1, self.size[0], self.size[1]

    def paint(self, display):
        if self.image:
            display.blit(self.image, (0, 0))
        else:
            pygame.draw.rect(display, (0, 0, 200), self.get_rect())


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

    def drag(self, drag_start_point, delta):
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

    def paint(self, display):
        def check_and_fill_uncovered_area():
            list_image_size = self.list_image.get_size()
            display_size = display.get_size()
            covered_height = (caption_height + list_image_size[1])
            uncovered_height = display_size[1] - covered_height
            if uncovered_height > 0:
                width = display_size[0]
                pygame.draw.rect(display, self.bg_color, (0, covered_height, width, uncovered_height))

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


class MonitorChangeOverlay(View):
    ARROW_HEIGHT_PERCENTAGE = .25
    ARROW_EDGE_MARGIN = 3

    def __init__(self, color=(0, 255, 0)):
        super(MonitorChangeOverlay, self).__init__()
        self.color = color
        self.left_arrow = None
        self.right_arrow = None
        self.show_left = False
        self.show_right = False

    def show_right_arrow(self):
        self.need_repaint = True
        self.show_right = True

    def show_left_arrow(self):
        self.need_repaint = True
        self.show_left = True

    def clear_arrows(self):
        self.need_repaint = True
        self.show_right = False
        self.show_left = False

    def start_view(self, size):
        def round_int(num):
            return int(round(num) - .5) + (num > 0)

        def build_arrows():
            arrow_half_height = round_int(size[1] * self.ARROW_HEIGHT_PERCENTAGE / 2)
            arrow_width = arrow_half_height * 2
            center_y = int(size[1] / 2)

            self.left_arrow = []
            x = self.ARROW_EDGE_MARGIN
            y = center_y
            self.left_arrow.append((x, y))
            x = self.ARROW_EDGE_MARGIN + arrow_width
            y = center_y - arrow_half_height
            self.left_arrow.append((x, y))
            x = self.ARROW_EDGE_MARGIN + arrow_width
            y = center_y + arrow_half_height
            self.left_arrow.append((x, y))

            self.right_arrow = []
            x = size[0] - self.ARROW_EDGE_MARGIN
            y = center_y
            self.right_arrow.append((x, y))
            x = size[0] - self.ARROW_EDGE_MARGIN - arrow_width
            y = center_y - arrow_half_height
            self.right_arrow.append((x, y))
            x = size[0] - self.ARROW_EDGE_MARGIN - arrow_width
            y = center_y + arrow_half_height
            self.right_arrow.append((x, y))

        super(MonitorChangeOverlay, self).start_view(size)
        build_arrows()

    def paint(self, display):
        if self.show_left:
            pygame.draw.polygon(display, self.color, self.left_arrow)
        if self.show_right:
            pygame.draw.polygon(display, self.color, self.right_arrow)
