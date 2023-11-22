"""
change a image to other three directions
"""
import pygame


def change_image(image, direction):
    if direction == "up":
        return image
    elif direction == "down":
        return pygame.transform.rotate(image, 180)
    elif direction == "left":
        return pygame.transform.rotate(image, 90)
    elif direction == "right":
        return pygame.transform.rotate(image, 270)
