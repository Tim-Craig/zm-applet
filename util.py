import pygame
from pygame import Surface


def close_stream_ignore_exception(stream):
    if stream:
        try:
            stream.close()
        except Exception:
            pass


def create_message_image(message, image_size):
    image = Surface(image_size)
    image.fill((0, 0, 200))
    font = pygame.font.SysFont("monospace", 12)
    render_txt = font.render(message, True, (255, 255, 255))
    msg_size = render_txt.get_size()
    x = (image_size[0] / 2) - (msg_size[0] / 2)
    y = (image_size[1] / 2) - (msg_size[1] / 2)
    image.blit(render_txt, (x, y))
    return image
