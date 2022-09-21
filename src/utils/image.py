import pygame.image

cached_images = {}


def get_image(filepath: str):
    if filepath in cached_images:
        return cached_images[filepath]

    image = pygame.image.load(filepath).convert_alpha()
    cached_images[filepath] = image
    return image
