import pygame


class Normal_bullet(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.bullet_up = pygame.image.load(
            '../image/bullet_up.png').convert_alpha()
        self.bullet_down = pygame.image.load(
            '../image/bullet_down.png').convert_alpha()
        self.bullet_left = pygame.image.load(
            '../image/bullet_left.png').convert_alpha()
        self.bullet_right = pygame.image.load(
            '../image/bullet_right.png').convert_alpha()

        self.direction = "up"
        self.speed = 6
        self.life = False
        self.strong = False

        self.bullet = self.bullet_up
        self.rect = self.bullet.get_rect()
        self.rect.left, self.rect.right = 3 + 12 * 24, 3 + 24 * 24

    def change_image(self, direction):
        # 根据方向改变子弹的图片
        self.direction = direction
        if self.direction == "up":
            self.bullet = self.bullet_up
        elif self.direction == "down":
            self.bullet = self.bullet_down
        elif self.direction == "left":
            self.bullet = self.bullet_left
        elif self.direction == "right":
            self.bullet = self.bullet_right

    def move(self):
        direction_dic = {
            "up": (0, -self.speed),
            "down": (0, self.speed),
            "left": (-self.speed, 0),
            "right": (self.speed, 0)
        }
        self.rect = self.rect.move(direction_dic[self.direction])
        if self.rect.top < 3:
            self.life = False
        if self.rect.bottom > 630 - 3:
            self.life = False
        if self.rect.left < 3:
            self.life = False
        if self.rect.right > 630 - 3:
            self.life = False


class Fire_bullet(Normal_bullet):
    def __init__(self) -> None:
        super().__init__()
        

