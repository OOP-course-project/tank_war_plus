import pygame
import bullet
import random
from collections import deque

random.seed(1)

tank_T1_0 = "../image/tank_T1_0.png"
tank_T1_1 = "../image/tank_T1_1.png"
tank_T1_2 = "../image/tank_T1_2.png"
tank_T2_0 = "../image/tank_T2_0.png"
tank_T2_1 = "../image/tank_T2_1.png"
tank_T2_2 = "../image/tank_T2_2.png"


class Player_tank(pygame.sprite.Sprite):
    def __init__(self, player_number) -> None:
        super().__init__()

        if player_number == 1:
            self.tank_L0_image = pygame.image.load(tank_T1_0).convert_alpha()
            self.tank_L1_image = pygame.image.load(tank_T1_1).convert_alpha()
            self.tank_L2_image = pygame.image.load(tank_T1_2).convert_alpha()

        if player_number == 2:
            self.tank_L0_image = pygame.image.load(tank_T2_0).convert_alpha()
            self.tank_L1_image = pygame.image.load(tank_T2_1).convert_alpha()
            self.tank_L2_image = pygame.image.load(tank_T2_2).convert_alpha()

        self.frame = 0
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
        self.bullets_list = []
        self.direction = "up"
        self.direction_dic = {
            "up": (0, -self.speed),
            "down": (0, self.speed),
            "left": (-self.speed, 0),
            "right": (self.speed, 0),
        }

        self.max_life = 3
        self.health_bar_length = 48
        self.health_bar_color = (255, 0, 0, 255)

    def draw_health_bar(self, screen):
        health_bar_width = int((self.life / self.max_life) * self.health_bar_length)
        health_bar_surface = pygame.Surface((self.health_bar_length, 5))
        pygame.draw.rect(
            health_bar_surface, self.health_bar_color, (0, 0, health_bar_width, 5)
        )

        health_bar_position = (
            self.rect.centerx - self.health_bar_length / 2,
            self.rect.centery - 30,
        )

        screen.blit(health_bar_surface, health_bar_position)

    def shoot(self):
        new_bullet = random.choice(
            [bullet.Normal_bullet()] * 3
            + [bullet.Fire_bullet()]
            + [bullet.Freeze_bullet()]
        )
        new_bullet.life = True
        # 根据坦克的方向来确定子弹的方向
        new_bullet.change_image(self.direction)
        # 根据坦克的方向来确定子弹的位置
        if self.direction == "up":
            new_bullet.rect.left = self.rect.left + 20
            new_bullet.rect.bottom = self.rect.top - 1
        elif self.direction == "down":
            new_bullet.rect.left = self.rect.left + 20
            new_bullet.rect.top = self.rect.bottom + 1
        elif self.direction == "left":
            new_bullet.rect.right = self.rect.left - 1
            new_bullet.rect.top = self.rect.top + 20
        elif self.direction == "right":
            new_bullet.rect.left = self.rect.right + 1
            new_bullet.rect.top = self.rect.top + 20

        self.bullets_list.append(new_bullet)

    def move_func(self, tank_group, brick_group, iron_group):
        self.rect = self.rect.move(self.direction_dic[self.direction])
        if self.direction == "up":
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
            if self.rect.top < 3:
                self.rect = self.rect.move(self.direction_dic["down"])
                return True
        if self.direction == "down":
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
            if self.rect.bottom > 630 - 3:
                self.rect = self.rect.move(self.direction_dic["up"])
                return True
        if self.direction == "left":
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))
            if self.rect.left < 3:
                self.rect = self.rect.move(self.direction_dic["right"])
                return True
        if self.direction == "right":
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))
            if self.rect.right > 630 - 3:
                self.rect = self.rect.move(self.direction_dic["left"])
                return True
        if (
            pygame.sprite.spritecollide(
                self, brick_group, False, pygame.sprite.collide_rect_ratio(0.9)
            )
            or pygame.sprite.spritecollide(
                self, tank_group, False, pygame.sprite.collide_rect_ratio(0.9)
            )
            or pygame.sprite.spritecollide(
                self, iron_group, False, pygame.sprite.collide_rect_ratio(0.9)
            )
        ):
            dx, dy = self.direction_dic[self.direction]
            self.rect = self.rect.move(-dx, -dy)
            return True
        return False

    def update(self, screen):
        # if life is smaller than 0, kill the tank
        if self.life <= 0:
            self.kill()
        self.draw_health_bar(screen)
        for b in self.bullets_list:
            if not b.life:
                self.bullets_list.remove(b)


class Enemy_tank(pygame.sprite.Sprite):
    tank_id = 0

    def __init__(self, x=None, kind=None) -> None:
        super().__init__()
        Enemy_tank.tank_id = Enemy_tank.tank_id + 1
        self.tank_id = Enemy_tank.tank_id

        self.flash = False
        self.times = 90
        self.kind = kind
        if not kind:
            # self.kind = random.choice([1, 2, 3, 4])
            self.kind = (Enemy_tank.tank_id % 4) + 1

        if self.kind == 1:
            self.enemy_x_0 = pygame.image.load("../image/enemy_1_0.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load("../image/enemy_1_3.png").convert_alpha()
        if self.kind == 2:
            self.enemy_x_0 = pygame.image.load("../image/enemy_2_0.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load("../image/enemy_2_3.png").convert_alpha()
        if self.kind == 3:
            self.enemy_x_0 = pygame.image.load("../image/enemy_3_0.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load("../image/enemy_3_3.png").convert_alpha()
        if self.kind == 4:
            self.enemy_x_0 = pygame.image.load("../image/enemy_4_0.png").convert_alpha()
            self.enemy_x_3 = pygame.image.load("../image/enemy_4_3.png").convert_alpha()
        self.enemy_3_0 = pygame.image.load("../image/enemy_3_0.png").convert_alpha()
        self.enemy_3_2 = pygame.image.load("../image/enemy_3_2.png").convert_alpha()

        self.tank = self.enemy_x_0
        self.x = x

        if not self.x:
            # self.x = random.choice([1, 2, 3])
            self.x = (Enemy_tank.tank_id % 3) + 1
        self.x -= 1

        self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
        self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        self.rect = self.tank_R0.get_rect()
        self.rect.left, self.rect.top = 3 + self.x * 12 * 24, 3 + 24 * 0

        self.speed = 3
        self.original_speed = self.speed
        self.life = 2
        self.bullet_not_cooling = True
        self.bullet = bullet.Normal_bullet()
        self.dir_change = False
        self.direction = "down"
        self.direction_dic = {
            "up": (0, -self.speed),
            "down": (0, self.speed),
            "left": (-self.speed, 0),
            "right": (self.speed, 0),
        }
        self.slow_down = False
        self.slow_down_timer = 0
        self.in_fire = False
        self.in_fire_timer = 0
        self.in_fire_count = 0

        if self.kind == 2:
            self.speed = 5
            self.original_speed = 5
        if self.kind == 3:
            self.life = 3

        self.enemy_could_move = True

    def shoot(self):
        self.bullet.life = True
        self.bullet.change_image(self.direction)
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

        if self.direction == "up":
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        elif self.direction == "down":
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        elif self.direction == "left":
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))
        elif self.direction == "right":
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))

        if self.rect.top < 3:
            self.rect = self.rect.move(self.direction_dic["down"])
            self.direction = random.choice(["down", "left", "right"])
        elif self.rect.bottom > 630 - 3:
            self.rect = self.rect.move(self.direction_dic["up"])
            self.direction = random.choice(["up", "left", "right"])
        elif self.rect.left < 3:
            self.rect = self.rect.move(self.direction_dic["right"])
            self.direction = random.choice(["up", "down", "right"])
        elif self.rect.right > 630 - 3:
            self.rect = self.rect.move(self.direction_dic["left"])
            self.direction = random.choice(["up", "down", "left"])

        if (
            pygame.sprite.spritecollide(self, brick_group, False, None)
            or pygame.sprite.spritecollide(self, iron_group, False, None)
            or pygame.sprite.spritecollide(self, tank_group, False, None)
        ):
            self.rect = self.rect.move(
                -self.direction_dic[self.direction][0],
                -self.direction_dic[self.direction][1],
            )
            self.direction = random.choice(["up", "down", "left", "right"])

    def move_sync(self, direction, left, top):
        self.direction = direction
        self.rect.left = left
        self.rect.top = top

        if self.direction == "up":
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        elif self.direction == "down":
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        elif self.direction == "left":
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))
        elif self.direction == "right":
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))

    def update(self):
        if self.life <= 0:
            self.kill()
        pygame.display.update()

        # judge if the tank is in freeze
        if self.slow_down:
            self.speed = 1
        else:
            self.speed = self.original_speed

        # judge if the tank is in fire
        if self.in_fire and self.in_fire_count:
            if pygame.time.get_ticks() - self.in_fire_timer >= 500:
                self.in_fire_count -= 1
                self.life -= 0.25
                self.in_fire_timer = pygame.time.get_ticks()
                if self.in_fire_count == 0:
                    self.in_fire = False


class BFS_enemy_tank(Enemy_tank):
    def __init__(self, x=None, kind=None):
        super().__init__(x, kind)

        # 添加了3个用于记录坦克位置变化的变量
        self.last_pos = [self.rect.left, self.rect.top]
        self.stay_count = 0
        self.last_direction = self.direction
        self.disable_direction = set()
        self.found = False

    # bfs算法，用于计算下一步要走的点
    def bfs_search(self, start, goal, obstacles):
        """
        使用广度优先搜索算法，在避开障碍物的情况下，找到从起点到目标点的最短路径。

        Parameters:
        - start: 一个表示起点坐标的元组。坐标格式为 (x, y)。
        - goal: 一个表示目标点坐标的元组。坐标格式为 (x, y)。
        - obstacles: 一个表示要避开的障碍物坐标的集合。每个障碍物的坐标格式为 (x, y)。

        Returns:
        - shortest_path: 一个表示从起点到目标点的最短路径中各个点的坐标的列表。每个点的坐标格式为 (x, y)。
        """
        queue = deque([start])  # 使用双端队列作为搜索的数据结构，起点作为初始节点
        visited = set([start])  # 使用集合记录已访问过的节点
        path = {}  # 使用字典记录每个节点的父节点，以便回溯路径
        directions = [(0, -48), (0, 48), (-48, 0), (48, 0)]  # 上、下、左、右，表示四个方向移动的偏移量

        while queue:
            x, y = queue.popleft()  # 从队列的左侧取出一个节点进行处理
            if (x, y) == goal:
                # 回溯路径
                current = goal
                shortest_path = []
                while current != start:
                    shortest_path.append(current)  # 将当前节点添加到最短路径中
                    current = path.get(current, start)  # 获取当前节点的父节点

                return shortest_path[::-1]  # 返回最短路径的反向列表

            for dx, dy in directions:
                nx, ny = x + dx, y + dy  # 计算下一个节点的坐标
                if (nx, ny) in obstacles or nx < 0 or ny < 0 or nx >= 630 or ny >= 630:
                    continue  # 如果下一个节点是障碍物或超出边界，则跳过
                if (nx, ny) not in visited:
                    queue.append((nx, ny))  # 将下一个节点加入队列
                    visited.add((nx, ny))  # 将下一个节点标记为已访问
                    path[(nx, ny)] = (x, y)  # 记录下一个节点的父节点

    # 根据点确认移动方向
    def calculate_new_direction(self, start, path):
        """
        根据起始位置和给定的路径计算新的方向。

        参数:
            start (tuple): 起始位置，表示为一个元组 (x, y)。
            path (list): 表示路径的位置列表。

        返回:
            str 或 None: 新的方向，表示为字符串 "right"、"left"、"down"、"up"，如果没有路径则返回 None。
        """
        if not path:
            return None  # 如果路径为空，则返回 None，表示没有路径

        next_position = path[0]  # 取下一个位置

        dx, dy = (
            next_position[0] - start[0],
            next_position[1] - start[1],
        )  # 计算 x 和 y 的差值

        if dx > 0:
            return "right"  # 如果 x 的差值大于 0，表示向右移动
        elif dx < 0:
            return "left"  # 如果 x 的差值小于 0，表示向左移动
        elif dy > 0:
            return "down"  # 如果 y 的差值大于 0，表示向下移动
        elif dy < 0:
            return "up"  # 如果 y 的差值小于 0，表示向上移动

        return None  # 如果上述条件都不满足，则返回 None，表示没有方向

    # 添加了obstacles参数，用于传入所有坦克共享的障碍物坐标集合
    def move(self, tank_group, brick_group, iron_group, obstacles):
        """
        根据当前位置、障碍物和其他坦克移动坦克。

        参数:
        tank_group (Group): 包含当前坦克的坦克组。
        brick_group (Group): 砖块组。
        iron_group (Group): 铁障碍物组。
        obstacles (set): 应避免的障碍物集合。

        返回:
        无

        描述:
        - 移除具有与当前坦克相同坐标的障碍物。
        - 根据当前位置，在坦克周围添加障碍物。
        - 更新玩家坦克、敌方坦克、砖块和铁障碍物的列表。
        - 找到最近的敌方坦克的位置。
        - 找到最近的玩家坦克的位置。
        - 执行BFS搜索以找到最短路径到最近的玩家坦克。
        - 根据BFS搜索结果计算新的移动方向。
        - 根据敌方坦克相对于玩家坦克的位置更新坦克的水平和垂直方向。
        - 如果坦克保持相同方向时间过长，则更改方向。
        - 根据当前方向移动坦克。
        - 更新坦克的上一个位置和方向。
        - 根据当前方向更新坦克的图像。
        - 如果坦克与砖块、铁障碍物或其他坦克发生碰撞，则向相反方向移动坦克复原其位置。
        """

        ##此处为新增代码起始###############################

        # 去除集合中和当前坦克坐标一样的值
        popobstacles = set()

        # 坦克的左右两侧
        for i in range(self.rect.left, self.rect.right):
            obstacles.add((i, self.rect.top))
            obstacles.add((i, self.rect.bottom))
        # 坦克的上下两侧
        for i in range(self.rect.top, self.rect.bottom):
            obstacles.add((self.rect.left, i))
            obstacles.add((self.rect.top, i))
        # 从障碍物中排除当前坦克
        obstacles = obstacles - popobstacles

        # 存储玩家坦克、敌方坦克、砖块和铁障碍物的位置信息列表
        player_list = []
        enemy_list = []
        brick_list = []
        iron_list = []

        # 获取所有坦克的位置信息
        for tank in tank_group.sprites():
            if isinstance(tank, Player_tank):
                player_list.append(
                    (tank.rect.left, tank.rect.top, tank.rect.right, tank.rect.bottom)
                )
            else:
                enemy_list.append(
                    (tank.rect.left, tank.rect.top, tank.rect.right, tank.rect.bottom)
                )

        # 获取所有砖块的位置信息
        for brick in brick_group:
            brick_list.append(
                (brick.rect.left, brick.rect.top, brick.rect.right, brick.rect.bottom)
            )

        # 获取所有铁障碍物的位置信息
        for iron in iron_group:
            iron_list.append(
                (iron.rect.left, iron.rect.top, iron.rect.right, iron.rect.bottom)
            )

        # 找到当前敌方坦克的位置
        enemy_tank_position = (self.rect.left, self.rect.top)

        # 寻找最近玩家坦克的位置
        closest_player_tank = None
        min_distance = float("inf")
        for player in player_list:
            distance = abs(player[0] - enemy_tank_position[0]) + abs(
                player[1] - enemy_tank_position[1]
            )
            if distance < min_distance:
                min_distance = distance
                closest_player_tank = (player[0], player[1])

        if closest_player_tank:
            # 执行BFS搜索找到最近的友方坦克
            path = self.bfs_search(enemy_tank_position, closest_player_tank, obstacles)

            # 根据BFS搜索的结果来更新移动方向
            new_direction = self.calculate_new_direction(enemy_tank_position, path)
            if new_direction:
                self.direction = new_direction

            # 根据敌方坦克相对于玩家坦克的位置更新坦克备选的水平和垂直移动方向
            if enemy_tank_position[0] - player[0] <= 0:
                self.h_direction = "right"
            else:
                self.h_direction = "left"
            if enemy_tank_position[1] - player[1] <= 0:
                self.v_direction = "down"
            else:
                self.v_direction = "up"

        # 如果坦克保持相同方向时间过长，则更改方向
        # print(self.disable_direction)
        if self.stay_count > 10 and self.last_direction == self.direction:
            directions = set(["up", "down", "left", "right"])
            able_directions = list(directions - self.disable_direction)

            if self.h_direction in able_directions:
                self.direction = self.h_direction
            elif self.v_direction in able_directions:
                self.direction = self.v_direction
            else:
                self.direction = random.choice(able_directions)

            self.direction = (
                self.h_direction
                if self.last_direction in ["up", "down"]
                else self.v_direction
            )

            # self.direction = self.v_direction

            self.stay_count -= 7

        if self.found:
            self.direction = self.last_direction

        # 从函数开头移动到确认移动方向后再移动
        self.rect = self.rect.move(self.direction_dic[self.direction])

        ##此处为新增代码结束###############################

        if self.direction == "up":
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        elif self.direction == "down":
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        elif self.direction == "left":
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))
        elif self.direction == "right":
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))

        if self.rect.top < 3:
            self.rect = self.rect.move(self.direction_dic["down"])
            self.direction = random.choice(["down", "left", "right"])
        elif self.rect.bottom > 630 - 3:
            self.rect = self.rect.move(self.direction_dic["up"])
            self.direction = random.choice(["up", "left", "right"])
        elif self.rect.left < 3:
            self.rect = self.rect.move(self.direction_dic["right"])
            self.direction = random.choice(["up", "down", "right"])
        elif self.rect.right > 630 - 3:
            self.rect = self.rect.move(self.direction_dic["left"])
            self.direction = random.choice(["up", "down", "left"])

        if (
            pygame.sprite.spritecollide(
                self, brick_group, False, pygame.sprite.collide_rect_ratio(0.9)
            )
            or pygame.sprite.spritecollide(
                self, iron_group, False, pygame.sprite.collide_rect_ratio(0.9)
            )
            or pygame.sprite.spritecollide(
                self, tank_group, False, pygame.sprite.collide_rect_ratio(0.9)
            )
        ):
            # print(pygame.sprite.spritecollide(self, tank_group, False, pygame.sprite.collide_rect_ratio(0.9)))

            for tank in pygame.sprite.spritecollide(
                self, tank_group, False, pygame.sprite.collide_rect_ratio(0.9)
            ):
                if isinstance(tank, Player_tank):
                    self.found = True
                    break

            self.rect = self.rect.move(
                -self.direction_dic[self.direction][0],
                -self.direction_dic[self.direction][1],
            )

            if not self.found:
                self.disable_direction.add(self.direction)

            # 注释了之前因碰撞随机重置方向的代码
            # self.direction = random.choice(["up", "down", "left", "right"])
        else:
            self.found = False

        # 更新坦克停留时间
        if (
            abs(self.rect.left - self.last_pos[0]) < 3
            and abs(self.rect.top - self.last_pos[1]) < 3
        ):
            self.stay_count += 1
        else:
            self.disable_direction = set()

        # 更新坦克上一次移动位置的信息
        self.last_pos[0] = self.rect.left
        self.last_pos[1] = self.rect.top
        self.last_direction = self.direction


if __name__ == "__main__":
    pass
