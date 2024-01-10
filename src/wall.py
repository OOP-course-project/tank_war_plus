import json
import pygame

brick_image = pygame.image.load(r"../image/brick.png")
iron_image = pygame.image.load(r"../image/iron.png")


class Brick(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = brick_image
        self.rect = self.image.get_rect()


class Iron(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = iron_image
        self.rect = self.image.get_rect()


class Map:
    def __init__(self, map_file):
        self.brick_group = pygame.sprite.Group()
        self.iron_group = pygame.sprite.Group()

        # 加载地图数据
        with open(map_file, "r") as file:
            map_data = json.load(file)

        # 用加载的数据创建砖块
        for brick_data in map_data["bricks"]:
            self.brick = Brick()
            self.brick.rect.left, self.brick.rect.top = (
                3 + brick_data["x"] * 24,
                3 + brick_data["y"] * 24,
            )
            self.brick_group.add(self.brick)

        # 用加载的数据创建铁块
        for iron_data in map_data["irons"]:
            self.iron = Iron()
            self.iron.rect.left, self.iron.rect.top = (
                3 + iron_data["x"] * 24,
                3 + iron_data["y"] * 24,
            )
            self.iron_group.add(self.iron)


class home(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"../image/home.png").convert_alpha()
        self.home_destroyed_image = pygame.image.load(
            r"../image/home_destroyed.png"
        ).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = 3 + 12 * 24, 3 + 24 * 24
        self.life = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if not self.life:
            screen.blit(self.home_destroyed_image, self.rect)


if __name__ == "__main__":
    map = Map("../maps/initial_points.json")
