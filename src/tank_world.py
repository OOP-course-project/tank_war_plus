import pygame
import sys
import wall
import tank
import food
import bullet
import pygame


class Tank_world:
    def __init__(self, screen, double_players=False) -> None:
        self.screen = screen
        self.double_players = double_players
        self.clock = pygame.time.Clock()
        self.game_over = False

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
        self.bang_sound.set_volume(1)
        self.start_sound.play()

        self.all_tank_group = pygame.sprite.Group()
        self.player_tank_group = pygame.sprite.Group()
        self.enemy_tank_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()

        self.back_ground = wall.Map()
        # self.foods = food.Food()

        self.player_tank1 = tank.Player_tank(1)
        self.all_tank_group.add(self.player_tank1)
        self.player_tank_group.add(self.player_tank1)

        if self.double_players:
            self.player_tank2 = tank.Player_tank(2)
            self.all_tank_group.add(self.player_tank2)
            self.player_tank_group.add(self.player_tank2)

        for i in range(1, 4):
            enemy = tank.Enemy_tank(i)
            self.all_tank_group.add(enemy)
            self.enemy_tank_group.add(enemy)

        # enemy tank appearance image
        self.appearance = []
        self.appearance.append(self.enemy_appear.subsurface((0, 0), (48, 48)))
        self.appearance.append(self.enemy_appear.subsurface((48, 0), (48, 48)))
        self.appearance.append(self.enemy_appear.subsurface((96, 0), (48, 48)))

        # custom events
        self.DELAYEVENT = pygame.constants.USEREVENT
        pygame.time.set_timer(self.DELAYEVENT, 200)
        self.ENEMYBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 1
        pygame.time.set_timer(self.ENEMYBULLETNOTCOOLINGEVENT, 1000)
        self.PLAYERBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 2
        self.NOTMOVEEVENT = pygame.constants.USEREVENT + 3
        pygame.time.set_timer(self.NOTMOVEEVENT, 8000)

        self.current_time = pygame.time.get_ticks()
        self.delay = 100
        self.moving1 = 0
        self.score1 = 0
        self.running_T1 = True
        self.last_player_shot_time_T1 = 0
        if self.double_players:
            self.moving2 = 0
            self.score2 = 0
            self.running_T2 = True
            self.last_player_shot_time_T2 = 0
        self.enemy_could_move = True
        self.switch_R1_R2_image = True
        self.home_survive = True

    def tank_moving(
        self,
        player_tank,
        direction,
    ):
        if player_tank == self.player_tank1:
            self.moving1 = 7
            self.running_T1 = True
        elif player_tank == self.player_tank2:
            self.moving2 = 7
            self.running_T2 = True
        player_tank.direction = direction
        self.all_tank_group.remove(player_tank)
        if player_tank.move_func(
            self.all_tank_group,
            self.back_ground.brick_group,
            self.back_ground.iron_group,
        ):
            if player_tank == self.player_tank1:
                self.moving1 = 0
            elif player_tank == self.player_tank2:
                self.moving2 = 0
        self.all_tank_group.add(player_tank)

    def tank_shoot(self, player_tank):
        if player_tank == self.player_tank1:
            if self.current_time - self.last_player_shot_time_T1 >= 500:
                self.fire_sound.play()
                player_tank.shoot()
                player_tank.bullet_not_cooling = True
                if player_tank == self.player_tank1:
                    self.last_player_shot_time_T1 = self.current_time
                elif player_tank == self.player_tank2:
                    self.last_player_shot_time_T2 = self.current_time
        elif player_tank == self.player_tank2:
            if self.current_time - self.last_player_shot_time_T2 >= 500:
                self.fire_sound.play()
                player_tank.shoot()
                player_tank.bullet_not_cooling = True
                if player_tank == self.player_tank1:
                    self.last_player_shot_time_T1 = self.current_time
                elif player_tank == self.player_tank2:
                    self.last_player_shot_time_T2 = self.current_time

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == self.PLAYERBULLETNOTCOOLINGEVENT:
                # player tank bullet cooling 0.5s
                if self.current_time - self.last_player_shot_time_T1 >= 500:
                    self.player_tank1.bullet_not_cooling = True
                if self.current_time - self.last_player_shot_time_T2 >= 500:
                    self.player_tank2.bullet_not_cooling = True

            if event.type == self.ENEMYBULLETNOTCOOLINGEVENT:
                for enemy in self.enemy_tank_group:
                    enemy.bullet_not_cooling = True

            if event.type == self.NOTMOVEEVENT:
                self.enemy_could_move = True

            if event.type == self.DELAYEVENT:
                if len(self.enemy_tank_group) < 4:
                    enemy = tank.Enemy_tank()
                    if pygame.sprite.spritecollide(
                        enemy, self.all_tank_group, False, None
                    ):
                        break
                    self.all_tank_group.add(enemy)
                    self.enemy_tank_group.add(enemy)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and pygame.KMOD_CTRL:
                    pygame.quit()
                    sys.exit()

    def update(self):
        self.current_time = pygame.time.get_ticks()
        self.handle_events()
        self.player_tank_group.update(self.screen)
        self.enemy_tank_group.update()
        for enemy_tank in self.enemy_tank_group:
            if enemy_tank.slow_down:
                if self.current_time - enemy_tank.slow_down_timer >= 5000:
                    enemy_tank.slow_down = False
        if len(self.player_tank_group) == 0:
            self.game_over = True

        self.draw(self.current_time)

    def run(self):
        while not self.game_over:
            self.current_time = pygame.time.get_ticks()
            self.handle_events()
            # update the state of player tank
            self.player_tank_group.update(self.screen)
            self.enemy_tank_group.update()

            for enemy_tank in self.enemy_tank_group:
                if enemy_tank.slow_down:
                    if self.current_time - enemy_tank.slow_down_timer >= 5000:
                        enemy_tank.slow_down = False
            if len(self.player_tank_group) == 0:
                self.game_over = True

            self.control(self.current_time)
            self.draw(self.current_time)

            self.delay -= 1

            if not self.delay:
                self.delay = 100

            pygame.display.flip()
            self.clock.tick(60)
            if self.game_over:
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                self.__init__(self.screen, self.double_players)
                                self.run()

    def control(self, current_time):
        # player 1 control
        key_pressed = pygame.key.get_pressed()
        if self.player_tank1.life > 0:
            if self.moving1:
                self.moving1 -= 1
                self.all_tank_group.remove(self.player_tank1)
                if self.player_tank1.move_func(
                    self.all_tank_group,
                    self.back_ground.brick_group,
                    self.back_ground.iron_group,
                ):
                    self.moving1 += 1
                self.all_tank_group.add(self.player_tank1)
                self.running_T1 = True
            if not self.moving1:
                if key_pressed[pygame.K_w]:
                    self.tank_moving(self.player_tank1, "up")

                elif key_pressed[pygame.K_s]:
                    self.tank_moving(self.player_tank1, "down")
                elif key_pressed[pygame.K_a]:
                    self.tank_moving(self.player_tank1, "left")
                elif key_pressed[pygame.K_d]:
                    self.tank_moving(self.player_tank1, "right")
            if key_pressed[pygame.K_j]:
                self.tank_shoot(self.player_tank1)

        if self.double_players:
            if self.player_tank2.life > 0:
                # player 2 moving
                if self.moving2:
                    self.moving2 -= 1
                    self.all_tank_group.remove(self.player_tank2)
                    if self.player_tank2.move_func(
                        self.all_tank_group,
                        self.back_ground.brick_group,
                        self.back_ground.iron_group,
                    ):
                        self.moving2 += 1
                    self.all_tank_group.add(self.player_tank2)
                    self.running_T2 = True
                else:
                    if key_pressed[pygame.K_UP]:
                        self.tank_moving(self.player_tank2, "up")
                    elif key_pressed[pygame.K_DOWN]:
                        self.tank_moving(self.player_tank2, "down")
                    elif key_pressed[pygame.K_LEFT]:
                        self.tank_moving(self.player_tank2, "left")
                    elif key_pressed[pygame.K_RIGHT]:
                        self.tank_moving(self.player_tank2, "right")
                if key_pressed[pygame.K_KP0]:
                    self.tank_shoot(self.player_tank2)

    def draw(self, current_time):
        # draw the background
        self.screen.blit(self.background_image, (0, 0))
        # draw brick and iron
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

        if not (self.delay % 5):
            self.switch_R1_R2_image = not self.switch_R1_R2_image

        # show player score
        font = pygame.font.Font(None, 36)
        score_text1 = font.render(f"Score1: {self.score1}", True, (255, 255, 255))
        self.screen.blit(score_text1, (10, 10))
        if self.double_players:
            score_text2 = font.render(f"Score2: {self.score2}", True, (255, 255, 255))
            self.screen.blit(
                score_text2,
                (self.screen.get_width() - score_text2.get_width() - 10, 10),
            )

        # draw player tank
        if self.player_tank1.life > 0:
            if self.switch_R1_R2_image and self.running_T1:
                self.screen.blit(
                    self.player_tank1.tank_R1,
                    (self.player_tank1.rect.left, self.player_tank1.rect.top),
                )
                self.running_T1 = False
            else:
                self.screen.blit(
                    self.player_tank1.tank_R0,
                    (self.player_tank1.rect.left, self.player_tank1.rect.top),
                )
                if pygame.sprite.spritecollide(
                    self.player_tank1, self.back_ground.brick_group, False, None
                ) or pygame.sprite.spritecollide(
                    self.player_tank1, self.back_ground.iron_group, False, None
                ):
                    self.moving1 = 0

        if self.double_players:
            if self.player_tank2.life > 0:
                if self.switch_R1_R2_image and self.running_T2:
                    self.screen.blit(
                        self.player_tank2.tank_R0,
                        (self.player_tank2.rect.left, self.player_tank2.rect.top),
                    )
                    self.running_T2 = False
                else:
                    self.screen.blit(
                        self.player_tank2.tank_R1,
                        (self.player_tank2.rect.left, self.player_tank2.rect.top),
                    )

                if pygame.sprite.spritecollide(
                    self.player_tank2, self.back_ground.brick_group, False, None
                ) or pygame.sprite.spritecollide(
                    self.player_tank2, self.back_ground.iron_group, False, None
                ):
                    self.moving2 = 0

        self.player_tank_group.update(self.screen)

        for enemy_tank in self.enemy_tank_group:
            if enemy_tank.flash:
                if self.switch_R1_R2_image:
                    self.screen.blit(
                        enemy_tank.tank_R0,
                        (enemy_tank.rect.left, enemy_tank.rect.top),
                    )
                    if self.enemy_could_move:
                        self.all_tank_group.remove(enemy_tank)
                        enemy_tank.move(
                            self.all_tank_group,
                            self.back_ground.brick_group,
                            self.back_ground.iron_group,
                        )
                        self.all_tank_group.add(enemy_tank)
                else:
                    self.screen.blit(
                        enemy_tank.tank_R1,
                        (enemy_tank.rect.left, enemy_tank.rect.top),
                    )
                    if self.enemy_could_move:
                        self.all_tank_group.remove(enemy_tank)
                        enemy_tank.move(
                            self.all_tank_group,
                            self.back_ground.brick_group,
                            self.back_ground.iron_group,
                        )
                        self.all_tank_group.add(enemy_tank)
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
                    enemy_tank.flash = True

        # draw player 1 bullet
        for p1_bullet in self.player_tank1.bullets_list:
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
                            enemy_tank.slow_down_timer = current_time
                            enemy_tank.update()
                        if isinstance(p1_bullet, bullet.Fire_bullet):
                            enemy_tank.in_fire = True
                            enemy_tank.in_fire_count = 4
                            enemy_tank.in_fire_timer = current_time
                            enemy_tank.update()
                        self.bang_sound.play()
                        p1_bullet.life = False
                        p1_bullet.kill()
                        if enemy_tank.life == 1:
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
        if self.double_players:
            for p2_bullet in self.player_tank2.bullets_list:
                if p2_bullet.life:
                    p2_bullet.move()
                    self.screen.blit(p2_bullet.bullet, p2_bullet.rect)

                    # bullet hit enemy bullet
                    for enemy_bullet in self.enemy_bullet_group:
                        if enemy_bullet.life:
                            if pygame.sprite.collide_rect(p2_bullet, enemy_bullet):
                                p2_bullet.life = False
                                enemy_bullet.life = False
                                pygame.sprite.spritecollide(
                                    p2_bullet, self.enemy_bullet_group, True, None
                                )

                    # bullet hit enemy tank
                    for enemy_tank in self.enemy_tank_group:
                        if pygame.sprite.collide_rect(p2_bullet, enemy_tank):
                            if isinstance(p2_bullet, bullet.Freeze_bullet):
                                enemy_tank.slow_down = True
                                enemy_tank.slow_down_timer = current_time
                                enemy_tank.update()
                            if isinstance(p2_bullet, bullet.Fire_bullet):
                                enemy_tank.in_fire = True
                                enemy_tank.in_fire_count = 4
                                enemy_tank.in_fire_timer = current_time
                                enemy_tank.update()
                            self.bang_sound.play()
                            p2_bullet.life = False
                            p2_bullet.kill()
                            if enemy_tank.life == 1:
                                self.score2 += 1
                            enemy_tank.life -= 1

                    # bullet hit brick
                    if pygame.sprite.spritecollide(
                        p2_bullet, self.back_ground.brick_group, True, None
                    ):
                        p2_bullet.life = False
                        p2_bullet.rect.left, p2_bullet.rect.top = (
                            3 + 12 * 24,
                            3 + 24 * 24,
                        )

                    # bullet hit iron
                    if pygame.sprite.spritecollide(
                        p2_bullet, self.back_ground.iron_group, False, None
                    ):
                        p2_bullet.life = False
                        p2_bullet.rect.left, p2_bullet.rect.top = (
                            3 + 12 * 24,
                            3 + 24 * 24,
                        )

        # draw enemy bullet
        for enemy_tank in self.enemy_tank_group:
            # if enemy bullet not life, then enemy tank shoot
            if (
                not enemy_tank.bullet.life
                and enemy_tank.bullet_not_cooling
                and self.enemy_could_move
            ):
                self.enemy_bullet_group.remove(enemy_tank.bullet)
                enemy_tank.shoot()
                self.enemy_bullet_group.add(enemy_tank.bullet)
                enemy_tank.bullet_not_cooling = False
            # if the sound is playing, then draw bullet
            if enemy_tank.flash:
                if enemy_tank.bullet.life:
                    # if enemy can move
                    if self.enemy_could_move:
                        enemy_tank.bullet.move()
                    self.screen.blit(enemy_tank.bullet.bullet, enemy_tank.bullet.rect)

                    # if bullet hit player tank
                    if (
                        pygame.sprite.collide_rect(enemy_tank.bullet, self.player_tank1)
                        and self.player_tank1 in self.player_tank_group
                    ):
                        self.player_tank1.life -= 1
                        enemy_tank.bullet.life = False
                        self.bang_sound.play()
                        moving1 = 0
                    if self.double_players:
                        if (
                            pygame.sprite.collide_rect(
                                enemy_tank.bullet, self.player_tank2
                            )
                            and self.player_tank2 in self.player_tank_group
                        ):
                            self.player_tank2.life -= 1
                            enemy_tank.bullet.life = False
                            self.bang_sound.play()
                            moving2 = 0

                    # if bullet hit brick
                    if pygame.sprite.spritecollide(
                        enemy_tank.bullet, self.back_ground.brick_group, True, None
                    ):
                        enemy_tank.bullet.life = False
                    # if bullet hit iron
                    if enemy_tank.bullet.strong:
                        if pygame.sprite.spritecollide(
                            enemy_tank.bullet, self.back_ground.iron_group, True, None
                        ):
                            enemy_tank.bullet.life = False
                    else:
                        if pygame.sprite.spritecollide(
                            enemy_tank.bullet, self.back_ground.iron_group, False, None
                        ):
                            enemy_tank.bullet.life = False

        if self.game_over:
            self.screen.fill((0, 0, 0))
            text = font.render("Game Over!", True, (255, 255, 255))
            text_rect = text.get_rect()
            score1_text = font.render(
                "Player 1 Score: " + str(self.score1), True, (255, 255, 255)
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
            if self.double_players:
                text_rect.center = (
                    self.screen.get_rect().centerx,
                    self.screen.get_rect().centery - 20,
                )
                self.screen.blit(text, text_rect)
                score2_text = font.render(
                    "Player 2 Score: " + str(self.score2), True, (255, 255, 255)
                )
                score1_rect = score1_text.get_rect()
                score2_rect = score2_text.get_rect()
                score1_rect.center = (
                    self.screen.get_rect().centerx,
                    self.screen.get_rect().centery,
                )
                score2_rect.center = (
                    self.screen.get_rect().centerx,
                    self.screen.get_rect().centery + 20,
                )
                self.screen.blit(score1_text, score1_rect)
                self.screen.blit(score2_text, score2_rect)

            text = font.render("Press space to play again.", True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (
                self.screen.get_rect().centerx,
                self.screen.get_rect().centery + 40,
            )
            self.screen.blit(text, text_rect)
            pygame.display.flip()

    def get_reward(self):
        return self.score1

    def is_game_over(self):
        return self.game_over


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((630, 630))
    tw1 = Tank_world(screen, double_players=False)
    tw1.run()