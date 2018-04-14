import pygame
from pygame import Surface


def close_stream_ignore_exception(stream):
    if stream:
        try:
            stream.close()
        except Exception:
            pass


def get_best_fitting_font(message, image_size):
    def is_font_size_overflow(font_size):
        font = pygame.font.SysFont("monospace", font_size)
        msg_size = font.size(message)
        if msg_size[0] > image_size[0] or msg_size[1] > image_size[1]:
            return True
        else:
            return False

    last_size = 1
    while not is_font_size_overflow(last_size + 1):
        last_size = last_size + 1

    return pygame.font.SysFont("monospace", last_size)


def create_message_image(message, image_size, x_margin_percent=10):
    image = Surface(image_size)
    margin_size = (image_size[0] - (image_size[0] * x_margin_percent / 100), image_size[1])
    image.fill((0, 0, 200))
    font = get_best_fitting_font(message, margin_size)
    render_txt = font.render(message, True, (255, 255, 255))
    msg_size = render_txt.get_size()
    x = (image_size[0] / 2) - (msg_size[0] / 2)
    y = (image_size[1] / 2) - (msg_size[1] / 2)
    image.blit(render_txt, (x, y))
    return image
