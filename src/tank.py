import pygame
import bullet
import random

tank_T1_0 = '../image/tank_T1_0.png'
tank_T1_1 = '../image/tank_T1_1.png'
tank_T1_2 = '../image/tank_T1_2.png'
tank_T2_0 = '../image/tank_T2_0.png'
tank_T2_1 = '../image/tank_T2_1.png'
tank_T2_2 = '../image/tank_T2_2.png'


class Player_tank(pygame.sprite.Sprite):
    def __init__(self, player_number) -> None:
        super().__init__()

        self.life = True
        if player_number == 1:
            self.tank_L0_image = pygame.image.load(tank_T1_0).convert_alpha()
            self.tank_L1_image = pygame.image.load(tank_T1_1).convert_alpha()
            self.tank_L2_image = pygame.image.load(tank_T1_2).convert_alpha()

        if player_number == 2:
            self.tank_L0_image = pygame.image.load(tank_T2_0).convert_alpha()
            self.tank_L1_image = pygame.image.load(tank_T2_1).convert_alpha()
            self.tank_L2_image = pygame.image.load(tank_T2_2).convert_alpha()

        self.level = 0
        self.tank = self.tank_L0_image
        self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
        self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        self.rect = self.tank_R0.get_rect()
        if player_number == 1:
            self.rect.left, self.rect.top = 3 + 24 * 8, 3 + 24 * 24
        if player_number == 2:
            self.rect.left, self.rect.top = 3 + 24 * 16, 3 + 24 * 24
        self.speed = 3
        self.life = 3
        self.bullet_not_cooling = True
        self.bullet = bullet.Normal_bullet()
        self.direction = "up"
        self.direction_dic = {
            "up": (0, -self.speed),
            "down": (0, self.speed),
            "left": (-self.speed, 0),
            "right": (self.speed, 0)
        }

    def shoot(self):
        self.bullet.life = True
        # 根据坦克的方向来确定子弹的方向
        self.bullet.change_image(self.direction)
        # 根据坦克的方向来确定子弹的位置
        if self.direction == "up":
            self.bullet.rect.left = self.rect.left + 20
            self.bullet.rect.bottom = self.rect.top - 1
        elif self.direction == "down":
            self.bullet.rect.left = self.rect.left + 20
            self.bullet.rect.top = self.rect.bottom + 1
        elif self.direction == "left":
            self.bullet.rect.right = self.rect.left - 1
            self.bullet.rect.top = self.rect.top + 20
        elif self.direction == "right":
            self.bullet.rect.left = self.rect.right + 1
            self.bullet.rect.top = self.rect.top + 20

    def move_func(self, tank_group, brick_group, iron_group):
        self.rect = self.rect.move(self.direction_dic[self.direction])
        if self.direction == 'up':
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
            if self.rect.top < 3:
                self.rect = self.rect.move(self.direction_dic['down'])
                return True
        if self.direction == 'down':
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
            if self.rect.bottom > 630 - 3:
                self.rect = self.rect.move(self.direction_dic['up'])
                return True
        if self.direction == 'left':
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))
            if self.rect.left < 3:
                self.rect = self.rect.move(self.direction_dic['right'])
                return True
        if self.direction == 'right':
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))
            if self.rect.right > 630 - 3:
                self.rect = self.rect.move(self.direction_dic['left'])
                return True
        if pygame.sprite.spritecollide(self, brick_group, False, None) or pygame.sprite.spritecollide(self, iron_group, False, None):
            dx, dy = self.direction_dic[self.direction]
            self.rect = self.rect.move(-dx, -dy)
            return True
        if pygame.sprite.spritecollide(self, tank_group, False, None):
            dx, dy = self.direction_dic[self.direction]
            self.rect = self.rect.move(-dx, -dy)
            return True
        return False


class Enemy_tank(pygame.sprite.Sprite):
    def __init__(self, x=None, kind=None) -> None:
        super().__init__()

        self.flash = False
        self.times = 90
        self.kind = kind
        if not kind:
            self.kind = random.choice([1, 2, 3, 4])

        if self.kind == 1:
            self.enemy_x_0 = pygame.image.load(
                '../image/enemy_1_0.png').convert_alpha()
            self.enemy_x_3 = pygame.image.load(
                '../image/enemy_1_3.png').convert_alpha()
        if self.kind == 2:
            self.enemy_x_0 = pygame.image.load(
                '../image/enemy_2_0.png').convert_alpha()
            self.enemy_x_3 = pygame.image.load(
                '../image/enemy_2_3.png').convert_alpha()
        if self.kind == 3:
            self.enemy_x_0 = pygame.image.load(
                '../image/enemy_3_0.png').convert_alpha()
            self.enemy_x_3 = pygame.image.load(
                '../image/enemy_3_3.png').convert_alpha()
        if self.kind == 4:
            self.enemy_x_0 = pygame.image.load(
                '../image/enemy_4_0.png').convert_alpha()
            self.enemy_x_3 = pygame.image.load(
                '../image/enemy_4_3.png').convert_alpha()
        self.enemy_3_0 = pygame.image.load(
            '../image/enemy_3_0.png').convert_alpha()
        self.enemy_3_2 = pygame.image.load(
            '../image/enemy_3_2.png').convert_alpha()

        self.tank = self.enemy_x_0
        self.x = x

        if not self.x:
            self.x = random.choice([1, 2, 3])
        self.x -= 1

        self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
        self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        self.rect = self.tank_R0.get_rect()
        self.rect.left, self.rect.top = 3 + self.x * 12 * 24, 3 + 24 * 0

        self.speed = 1
        self.life = 1
        self.bullet_not_cooling = True
        self.bullet = bullet.Normal_bullet()
        self.dir_change = False
        self.direction = "down"
        self.direction_dic = {
            "up": (0, -self.speed),
            "down": (0, self.speed),
            "left": (-self.speed, 0),
            "right": (self.speed, 0)
        }

        if self.kind == 2:
            self.speed = 3
        if self.kind == 3:
            self.life = 3

    def shoot(self):
        self.bullet.life = True
        self.bullet.change_image(self.direction)
        self.bullet.speed = 16
        self.bullet.strong = False

        if self.direction == "up":
            self.bullet.rect.left = self.rect.left + 20
            self.bullet.rect.bottom = self.rect.top + 1
        elif self.direction == "down":
            self.bullet.rect.left = self.rect.left + 20
            self.bullet.rect.top = self.rect.bottom - 1
        elif self.direction == "left":
            self.bullet.rect.right = self.rect.left - 1
            self.bullet.rect.top = self.rect.top + 20
        elif self.direction == "right":
            self.bullet.rect.left = self.rect.right + 1
            self.bullet.rect.top = self.rect.top + 20

    def move(self, tank_group, brick_group, iron_group):
        self.rect = self.rect.move(self.direction_dic[self.direction])

        if self.direction == 'up':
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        elif self.direction == 'down':
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        elif self.direction == 'left':
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))
        elif self.direction == 'right':
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))

        if self.rect.top < 3:
            self.rect = self.rect.move(self.direction_dic['down'])
            self.direction = random.choice(['down', 'left', 'right'])
        elif self.rect.bottom > 630 - 3:
            self.rect = self.rect.move(self.direction_dic['up'])
            self.direction = random.choice(['up', 'left', 'right'])
        elif self.rect.left < 3:
            self.rect = self.rect.move(self.direction_dic['right'])
            self.direction = random.choice(['up', 'down', 'right'])
        elif self.rect.right > 630 - 3:
            self.rect = self.rect.move(self.direction_dic['left'])
            self.direction = random.choice(['up', 'down', 'left'])

        if pygame.sprite.spritecollide(self, brick_group, False, None) \
                or pygame.sprite.spritecollide(self, iron_group, False, None) \
                or pygame.sprite.spritecollide(self, tank_group, False, None):
            self.rect = self.rect.move(
                -self.direction_dic[self.direction][0], -self.direction_dic[self.direction][1])
            self.direction = random.choice(['up', 'down', 'left', 'right'])


if __name__ == "__main__":
    pass
