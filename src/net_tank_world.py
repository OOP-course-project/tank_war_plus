import pygame
import pygame_gui
import sys
import wall
import tank
import bullet
import random
from utilise import g

random.seed(1)


class Net_tank_world:
    globalV = {}  # 全局通用变量
    player_tanks_list = []  # 玩家坦克列表

    def __init__(
        self, screen, client=None, double_players: bool = False, MAX_PLAYER_NUM=2
    ):
        self.clock = pygame.time.Clock()
        self.client = client
        self.screen = screen
        self.MAX_PLAYER_NUM = MAX_PLAYER_NUM
        self.double_players = double_players
        self.background_image = pygame.image.load(
            r"../image/background.png"
        ).convert_alpha()
        self.home_image = pygame.image.load(r"../image/home.png").convert_alpha()
        self.home_destroyed_image = pygame.image.load(
            r"../image/home_destroyed.png"
        ).convert_alpha()
        self.bang_sound = pygame.mixer.Sound(r"../music/bang.wav")
        self.fire_sound = pygame.mixer.Sound(r"../music/Gunfire.wav")
        self.start_sound = pygame.mixer.Sound(r"../music/start.wav")
        self.enemy_appear = pygame.image.load(r"../image/appear.png").convert_alpha()

        # init gui
        self.gui_manager = pygame_gui.UIManager(
            (screen.get_width(), screen.get_height())
        )

        self.exit_popup = pygame_gui.windows.UIConfirmationDialog(
            rect=pygame.Rect(
                (
                    self.screen.get_rect().centerx - 100,
                    self.screen.get_rect().centery - 100,
                ),
                (200, 200),
            ),
            manager=self.gui_manager,
            window_title="Exit Confirmation",
            action_long_desc="Are you sure you want to exit?",
            action_short_name="exit",
            blocking=True,
        )
        self.exit_draw = False
        self.time_delta = self.clock.tick(60) / 1000.0
        self.exit_confirm = False
        tank.Enemy_tank.tank_id = 0

        Net_tank_world.globalV.clear()
        Net_tank_world.player_tanks_list.clear()
        for i in range(self.MAX_PLAYER_NUM):
            Net_tank_world.player_tanks_list.append(None)
        self.bang_sound.set_volume(1)
        self.start_sound.play()
        self.all_tank_group = pygame.sprite.Group()
        Net_tank_world.globalV["all_tank_group"] = self.all_tank_group
        self.player_tank_group = pygame.sprite.Group()
        Net_tank_world.globalV["player_tank_group"] = self.player_tank_group
        self.enemy_tank_group = pygame.sprite.Group()
        Net_tank_world.globalV["enemy_tank_group"] = self.enemy_tank_group
        self.enemy_bullet_group = pygame.sprite.Group()
        Net_tank_world.globalV["enemy_bullet_group"] = self.enemy_bullet_group
        self.back_ground = wall.Map("../maps/initial_points.json")
        Net_tank_world.globalV["back_ground"] = self.back_ground
        self.font = pygame.font.Font(None, 36)
        self.player_tank1 = None
        for i in range(self.MAX_PLAYER_NUM):
            Net_tank_world.player_tanks_list[i] = tank.Player_tank(i + 1)
            self.all_tank_group.add(self.player_tanks_list[i])
            self.player_tank_group.add(self.player_tanks_list[i])

            if i + 1 == g.player.role_id:
                self.player_tank1 = self.player_tanks_list[i]
                Net_tank_world.globalV["player_tank1"] = self.player_tank1

        for i in range(1, 4):
            enemy = tank.Enemy_tank(i)
            self.all_tank_group.add(enemy)
            self.enemy_tank_group.add(enemy)

        self.appearance = []

        self.appearance.append(self.enemy_appear.subsurface((0, 0), (48, 48)))
        self.appearance.append(self.enemy_appear.subsurface((48, 0), (48, 48)))
        self.appearance.append(self.enemy_appear.subsurface((96, 0), (48, 48)))

        self.DELAYEVENT = pygame.constants.USEREVENT
        pygame.time.set_timer(self.DELAYEVENT, 200)
        self.ENEMYBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 1
        pygame.time.set_timer(self.ENEMYBULLETNOTCOOLINGEVENT, 1000)
        self.PLAYERBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 2
        self.NOTMOVEEVENT = pygame.constants.USEREVENT + 3
        pygame.time.set_timer(self.NOTMOVEEVENT, 8000)

        self.delay = 100
        self.score1 = 0
        self.running_T1 = True
        self.last_player_shot_time_T1 = 0
        self.enemy_could_move = True
        self.switch_R1_R2_image = True
        self.home_survive = True

    def run(self):
        while not self.exit_confirm:
            self.current_time = pygame.time.get_ticks()

            if not g.game_start:
                self.screen.fill((0, 0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                pygame.display.flip()
                continue

            if not g.round_start:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == self.PLAYERBULLETNOTCOOLINGEVENT:
                    # player tank bullet cooling 0.5s
                    if self.current_time - self.last_player_shot_time_T1 >= 500:
                        self.player_tank1.bullet_not_cooling = True

                if event.type == self.ENEMYBULLETNOTCOOLINGEVENT:
                    for enemy in self.enemy_tank_group:
                        enemy.bullet_not_cooling = True

                if event.type == self.NOTMOVEEVENT:
                    self.enemy_could_move = True

                if event.type == self.DELAYEVENT:
                    if len(self.enemy_tank_group) < 3:
                        if g.player.role_id == 1:
                            enemy = tank.Enemy_tank()
                            if not pygame.sprite.spritecollide(
                                enemy, self.all_tank_group, False, None
                            ):
                                self.client.send(
                                    {
                                        "protocol": "enemy_birth",
                                        "tank_id": tank.Enemy_tank.tank_id,
                                    }
                                )

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c and pygame.KMOD_CTRL:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_ESCAPE:
                        self.exit_draw = not self.exit_draw

                if event.dict == {}:
                    continue

                self.gui_manager.process_events(event)

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                        if event.ui_element == self.exit_popup:
                            self.exit_confirm = True

            # update the status of player tank
            self.gui_manager.update(self.time_delta)
            self.player_tank_group.update(self.screen)
            self.enemy_tank_group.update()
            for enemy_tank in self.enemy_tank_group:
                if enemy_tank.slow_down:
                    if self.current_time - enemy_tank.slow_down_timer >= 5000:
                        enemy_tank.slow_down = False
            # check player keyboard control
            key_pressed = pygame.key.get_pressed()

            if len(self.player_tank_group) <= 0 or not g.game_start:
                if self.enemy_tanks_info:
                    # 告知服务端游戏结束
                    self.client.send({"protocol": "game_over"})

            # player 1 control
            if self.player_tank1.life > 0:
                # if not player_tank1.moving1:

                # 向服务端告知该玩家的操作（如玩家操作上下左右移动）
                if key_pressed[pygame.K_w]:
                    self.client.send(
                        {
                            "protocol": "cli_move",
                            "dir": "up",
                            "x": self.player_tank1.rect.x,
                            "y": self.player_tank1.rect.y,
                            "t": self.current_time,
                        }
                    )
                elif key_pressed[pygame.K_s]:
                    self.client.send(
                        {
                            "protocol": "cli_move",
                            "dir": "down",
                            "x": self.player_tank1.rect.x,
                            "y": self.player_tank1.rect.y,
                            "t": self.current_time,
                        }
                    )
                elif key_pressed[pygame.K_a]:
                    self.client.send(
                        {
                            "protocol": "cli_move",
                            "dir": "left",
                            "x": self.player_tank1.rect.x,
                            "y": self.player_tank1.rect.y,
                            "t": self.current_time,
                        }
                    )
                elif key_pressed[pygame.K_d]:
                    self.client.send(
                        {
                            "protocol": "cli_move",
                            "dir": "right",
                            "x": self.player_tank1.rect.x,
                            "y": self.player_tank1.rect.y,
                            "t": self.current_time,
                        }
                    )
                if key_pressed[pygame.K_j]:
                    if self.current_time - self.last_player_shot_time_T1 >= 500:
                        self.fire_sound.play()
                        # player_tank1.shoot()
                        # player_tank1.bullet_not_cooling = True
                        self.last_player_shot_time_T1 = self.current_time

                        # 告知服务器该玩家坦克发生射击动作
                        self.client.send({"protocol": "player_shoot"})

            self.client.send(
                {
                    "protocol": "player_pos",
                    "dir": self.player_tank1.direction,
                    "left": self.player_tank1.rect.left,
                    "top": self.player_tank1.rect.top,
                }
            )

            # draw background
            self.screen.blit(self.background_image, (0, 0))
            # draw bricks
            for brick in self.back_ground.brick_group:
                self.screen.blit(brick.image, brick.rect)
            # draw irons
            for iron in self.back_ground.iron_group:
                self.screen.blit(iron.image, iron.rect)
            # draw home
            if self.home_survive:
                self.screen.blit(self.home_image, (3 + 24 * 12, 3 + 24 * 24))
            else:
                self.screen.blit(self.home_destroyed_image, (3 + 24 * 12, 3 + 24 * 24))

            score_text1 = self.font.render(
                f"Your Score: {self.score1}", True, (255, 255, 255)
            )
            self.screen.blit(score_text1, (10, 10))

            # draw player tank

            for i in range(self.MAX_PLAYER_NUM):
                if Net_tank_world.player_tanks_list[i].life > 0:
                    self.screen.blit(
                        Net_tank_world.player_tanks_list[i].tank_R0,
                        (
                            Net_tank_world.player_tanks_list[i].rect.left,
                            Net_tank_world.player_tanks_list[i].rect.top,
                        ),
                    )
                    if pygame.sprite.spritecollide(
                        Net_tank_world.player_tanks_list[i],
                        self.back_ground.brick_group,
                        False,
                        None,
                    ) or pygame.sprite.spritecollide(
                        Net_tank_world.player_tanks_list[i],
                        self.back_ground.iron_group,
                        False,
                        None,
                    ):
                        Net_tank_world.player_tanks_list[i].moving1 = 0

            self.player_tank_group.update(self.screen)

            self.enemy_tanks_info = {}
            for enemy_tank in self.enemy_tank_group:
                if enemy_tank.flash:
                    self.screen.blit(
                        enemy_tank.tank_R1, (enemy_tank.rect.left, enemy_tank.rect.top)
                    )

                    if g.player.role_id == 1:
                        self.all_tank_group.remove(enemy_tank)
                        enemy_tank.move(
                            self.all_tank_group,
                            self.back_ground.brick_group,
                            self.back_ground.iron_group,
                        )
                        self.all_tank_group.add(enemy_tank)
                        self.enemy_tanks_info[enemy_tank.tank_id] = [
                            enemy_tank.direction,
                            enemy_tank.rect.left,
                            enemy_tank.rect.top,
                        ]

                else:
                    # show the enemy tank appearance
                    if enemy_tank.times > 0:
                        enemy_tank.times -= 1
                        if enemy_tank.times <= 10:
                            self.screen.blit(
                                self.appearance[2], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 20:
                            self.screen.blit(
                                self.appearance[1], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 30:
                            self.screen.blit(
                                self.appearance[0], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 40:
                            self.screen.blit(
                                self.appearance[2], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 50:
                            self.screen.blit(
                                self.appearance[1], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 60:
                            self.screen.blit(
                                self.appearance[0], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 70:
                            self.screen.blit(
                                self.appearance[2], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 80:
                            self.screen.blit(
                                self.appearance[1], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                        elif enemy_tank.times <= 90:
                            self.screen.blit(
                                self.appearance[0], (3 + enemy_tank.x * 12 * 24, 3)
                            )
                    if enemy_tank.times == 0:
                        if g.player.role_id == 1:
                            self.enemy_tanks_info[enemy_tank.tank_id] = [
                                enemy_tank.direction,
                                enemy_tank.rect.left,
                                enemy_tank.rect.top,
                            ]
                        enemy_tank.flash = True
            if g.player.role_id == 1 and self.enemy_tanks_info:
                # 告知服务端敌人发生移动，仅由1号玩家来告知服务端
                self.client.send(
                    {"protocol": "enemy_move", "info": self.enemy_tanks_info}
                )

            # draw player 1 bullet

            for i in range(self.MAX_PLAYER_NUM):
                for p1_bullet in Net_tank_world.player_tanks_list[i].bullets_list:
                    if p1_bullet.life:
                        p1_bullet.move()
                        self.screen.blit(p1_bullet.bullet, p1_bullet.rect)

                        # bullet hit enemy bullet
                        for enemy_bullet in self.enemy_bullet_group:
                            if enemy_bullet.life:
                                if pygame.sprite.collide_rect(p1_bullet, enemy_bullet):
                                    p1_bullet.life = False
                                    enemy_bullet.life = False
                                    pygame.sprite.spritecollide(
                                        p1_bullet, self.enemy_bullet_group, True, None
                                    )

                        # bullet hit enemy tank
                        for enemy_tank in self.enemy_tank_group:
                            if pygame.sprite.collide_rect(p1_bullet, enemy_tank):
                                if isinstance(p1_bullet, bullet.Freeze_bullet):
                                    enemy_tank.slow_down = True
                                    enemy_tank.slow_down_timer = self.current_time
                                    enemy_tank.update()
                                if isinstance(p1_bullet, bullet.Fire_bullet):
                                    enemy_tank.in_fire = True
                                    enemy_tank.in_fire_count = 4
                                    enemy_tank.in_fire_timer = self.current_time
                                    enemy_tank.update()
                                self.bang_sound.play()
                                p1_bullet.life = False
                                p1_bullet.kill()
                                if enemy_tank.life == 1 and (i + 1) == g.player.role_id:
                                    self.score1 += 1
                                enemy_tank.life -= 1

                        # bullet hit brick
                        if pygame.sprite.spritecollide(
                            p1_bullet, self.back_ground.brick_group, True, None
                        ):
                            p1_bullet.life = False
                            p1_bullet.rect.left, p1_bullet.rect.top = (
                                3 + 12 * 24,
                                3 + 24 * 24,
                            )

                        # bullet hit iron
                        if pygame.sprite.spritecollide(
                            p1_bullet, self.back_ground.iron_group, False, None
                        ):
                            p1_bullet.life = False
                            p1_bullet.rect.left, p1_bullet.rect.top = (
                                3 + 12 * 24,
                                3 + 24 * 24,
                            )

                        # bullet hit iron
                        if pygame.sprite.spritecollide(
                            p1_bullet, self.back_ground.iron_group, False, None
                        ):
                            p1_bullet.life = False
                            p1_bullet.rect.left, p1_bullet.rect.top = (
                                3 + 12 * 24,
                                3 + 24 * 24,
                            )

            # draw enemy bullet
            for enemy_tank in self.enemy_tank_group:
                # if enemy bullet not life, then enemy tank shoot
                if g.player.role_id == 1:
                    if (
                        not enemy_tank.bullet.life
                        and enemy_tank.bullet_not_cooling
                        and self.enemy_could_move
                    ):
                        # 告知服务端敌人坦克发生射击动作，仅由1号玩家来告知服务端
                        self.client.send({"protocol": "enemy_shoot"})
                    # if the sound is playing, then draw bullet
                if enemy_tank.flash:
                    if enemy_tank.bullet.life:
                        # if enemy can move
                        enemy_tank.bullet.move()
                        self.screen.blit(
                            enemy_tank.bullet.bullet, enemy_tank.bullet.rect
                        )

                        # if bullet hit player tank

                        for i in range(self.MAX_PLAYER_NUM):
                            if (
                                pygame.sprite.collide_rect(
                                    enemy_tank.bullet,
                                    Net_tank_world.player_tanks_list[i],
                                )
                                and Net_tank_world.player_tanks_list[i]
                                in self.player_tank_group
                            ):
                                # 告知服务端玩家受到攻击，仅由1号玩家来告知服务端
                                if g.player.role_id == 1:
                                    self.client.send(
                                        {"protocol": "player_injured", "role_id": i + 1}
                                    )
                                # 若血量低于 0 ，则告知服务端该玩家已死亡
                                if Net_tank_world.player_tanks_list[i].life <= 1:
                                    self.client.send(
                                        {"protocol": "player_die", "role_id": i + 1}
                                    )
                                # player_tanks_list[i].life -= 1
                                enemy_tank.bullet.life = False
                                self.bang_sound.play()
                                Net_tank_world.player_tanks_list[i].moving1 = 0

                        # if bullet hit brick
                        if pygame.sprite.spritecollide(
                            enemy_tank.bullet, self.back_ground.brick_group, True, None
                        ):
                            enemy_tank.bullet.life = False
                        # if bullet hit iron
                        if enemy_tank.bullet.strong:
                            if pygame.sprite.spritecollide(
                                enemy_tank.bullet,
                                self.back_ground.iron_group,
                                True,
                                None,
                            ):
                                enemy_tank.bullet.life = False
                        else:
                            if pygame.sprite.spritecollide(
                                enemy_tank.bullet,
                                self.back_ground.iron_group,
                                False,
                                None,
                            ):
                                enemy_tank.bullet.life = False

            self.draw_gui()
            pygame.display.flip()

            self.delay -= 1
            if not self.delay:
                self.delay = 100
            self.clock.tick(60)

        if g.game_start and not g.round_start:
            self.screen.fill((0, 0, 0))
            text = self.font.render("Game Over!", True, (255, 255, 255))
            text_rect = text.get_rect()
            score1_text = self.font.render(
                "Your Score: " + str(self.score1), True, (255, 255, 255)
            )
            if not self.double_players:
                text_rect.center = (
                    self.screen.get_rect().centerx,
                    self.screen.get_rect().centery,
                )
                self.screen.blit(text, text_rect)
                score_rect = score1_text.get_rect()
                score_rect.center = (
                    self.screen.get_rect().centerx,
                    self.screen.get_rect().centery + 20,
                )
                self.screen.blit(score1_text, score_rect)

            text = self.font.render(
                "Player 1 Press space to play again.", True, (255, 255, 255)
            )
            text_rect = text.get_rect()
            text_rect.center = (
                self.screen.get_rect().centerx,
                self.screen.get_rect().centery + 40,
            )
            self.screen.blit(text, text_rect)
            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and g.player.role_id == 1:
                            # 由1号玩家告知服务端游戏开始
                            self.client.send({"protocol": "game_start"})
                            Net_tank_world(
                                self.screen, self.client, self.double_players
                            )
                if g.round_start:
                    Net_tank_world(self.screen, self.client, self.double_players)

    def draw_gui(self):
        # draw the exit popup
        if self.exit_draw:
            self.gui_manager.draw_ui(self.screen)
