import pygame


def change_image(image, direction):
    image = pygame.image.load(image)
    if direction == "up":
        # 把surface转换为图片
        image = pygame.transform.rotate(image, 0)
    elif direction == "down":
        image = pygame.transform.rotate(image, 180)
    elif direction == "left":
        image = pygame.transform.rotate(image, 90)
    elif direction == "right":
        image = pygame.transform.rotate(image, 270)

    return image


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
