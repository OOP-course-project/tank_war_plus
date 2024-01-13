import pygame
import random


def change_image(image, direction):
    if direction == "up":
        return image
    elif direction == "down":
        return pygame.transform.rotate(image, 180)
    elif direction == "left":
        return pygame.transform.rotate(image, 90)
    elif direction == "right":
        return pygame.transform.rotate(image, 270)


def init_ui_background():
    tank_background = pygame.image.load("../image/tank_background.png")
    return tank_background


class Global:
    """
    游戏的全局共享变量
    """

    __instance = None

    client = None  # 客户端对象
    player = None  # 玩家本身
    game_start = False  # 游戏是否开始
    round_start = False  # 游戏回合是否已开始

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance


g = Global()
