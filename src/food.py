import pygame
import random


class Food(pygame.sprite.Sprite):
    def __init__(self):
        self.food_images = [
            pygame.image.load(r"..\image\food_boom.png").convert_alpha(),
            pygame.image.load(r"..\image\food_clock.png").convert_alpha(),
            pygame.image.load(r"..\image\food_gun.png").convert_alpha(),
            pygame.image.load(r"..\image\food_iron.png").convert_alpha(),
            pygame.image.load(r"..\image\food_protect.png").convert_alpha(),
            pygame.image.load(r"..\image\food_star.png").convert_alpha(),
            pygame.image.load(r"..\image\food_tank.png").convert_alpha()
        ]
        self.kind = random.randint(1, 7)
        self.image = self.food_images[self.kind - 1]
        self.rect = self.image.get_rect()
        self.rect.left = self.rect.top = random.randint(100, 500)
        self.life = False

    def change(self):
        self.kind = random.randint(1, 7)
        self.image = self.food_images[self.kind - 1]
        self.rect.left = self.rect.top = random.randint(100, 500)
        self.life = True
