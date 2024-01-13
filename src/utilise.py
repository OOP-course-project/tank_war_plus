import pygame


def change_image(image, direction):
    pygame_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    if direction == "up":
        # 把surface转换为图片
        pass
    elif direction == "down":
        image = pygame.transform.rotate(pygame_image, 180)
    elif direction == "left":
        image = pygame.transform.rotate(pygame_image, 90)
    elif direction == "right":
        image = pygame.transform.rotate(pygame_image, 270)

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
