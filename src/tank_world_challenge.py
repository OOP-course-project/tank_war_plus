import pygame
import pygame_gui
import tank
import tank_world
import bullet
import wall
import random_map_generator
import sys


class Tank_world_Challenge(tank_world.Tank_world):
    def __init__(
        self,
        screen,
        map_path="../maps/initial_points.json",
        double_players=False,
        BFS_open=True,
    ) -> None:
        super().__init__(
            screen, map_path=map_path, double_players=double_players, BFS_open=BFS_open
        )
        self.level_cnt = 0
        self.map_generator = random_map_generator.generate_map(26, 26)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == self.PLAYERBULLETNOTCOOLINGEVENT:
                # player tank bullet cooling 0.5s
                if self.current_time - self.last_player_shot_time_T1 >= 500:
                    self.player_tank1.bullet_not_cooling = True
                if self.double_players:
                    if self.current_time - self.last_player_shot_time_T2 >= 500:
                        self.player_tank2.bullet_not_cooling = True

            if event.type == self.ENEMYBULLETNOTCOOLINGEVENT:
                for enemy in self.enemy_tank_group:
                    enemy.bullet_not_cooling = True

            if event.type == self.NOTMOVEEVENT:
                self.enemy_could_move = True

            if event.type == self.DELAYEVENT:
                if len(self.enemy_tank_group) < 4:
                    if self.BFS_open:
                        enemy = tank.BFS_enemy_tank()
                    else:
                        enemy = tank.Enemy_tank()

                    enemy.speed = self.level_cnt / 5 + 3

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
                if event.key == pygame.K_ESCAPE:
                    self.exit_draw = not self.exit_draw

            if event.dict == {}:
                continue

            self.gui_manager.process_events(event)

            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                if event.ui_element == self.exit_popup:
                    self.exit_confirm = True

    def run(self):
        self.start_sound.play()

        while not (self.game_over or self.exit_confirm):
            self.current_time = pygame.time.get_ticks()
            self.handle_events()
            self.gui_manager.update(self.time_delta)
            # update the state of player tank
            self.player_tank_group.update(self.screen)
            self.enemy_tank_group.update()

            for enemy_tank in self.enemy_tank_group:
                if enemy_tank.slow_down:
                    if self.current_time - enemy_tank.slow_down_timer >= 5000:
                        enemy_tank.slow_down = False
            if len(self.player_tank_group) == 0:
                self.game_over = True

            self.control()
            self.draw(self.current_time)
            self.draw_gui()
            pygame.display.flip()

            self.delay -= 1

            if not self.delay:
                self.delay = 100

            self.clock.tick(60)

            if self.score1 >= 5:
                self.map_path = "../maps/random_map.json"
                self.map_generator.randomly_generate_map()
                self.map_generator.save_map(self.map_path)
                self.level_cnt = self.level_cnt + 1
                self.screen.fill((0, 0, 0))
                font = pygame.font.Font(None, 36)
                congratulation_text = font.render(
                    f"Congratulations! Level {self.level_cnt} passed!",
                    True,
                    (255, 255, 255),
                )
                congratulation_rect = congratulation_text.get_rect()
                continue_text = font.render(
                    "Press SPACE to play the next level.", True, (255, 255, 255)
                )
                continue_rect = continue_text.get_rect()
                congratulation_rect.center = (
                    self.screen.get_rect().centerx,
                    self.screen.get_rect().centery,
                )
                continue_rect.center = (
                    self.screen.get_rect().centerx,
                    self.screen.get_rect().centery + 30,
                )
                self.screen.blit(continue_text, continue_rect)
                self.screen.blit(congratulation_text, congratulation_rect)
                pygame.display.flip()

                while self.score1 >= 5:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                level_cnt_temp = self.level_cnt  # 存储当前关卡计数值
                                if self.level_cnt > 0:
                                    self.__init__(
                                        screen=self.screen,
                                        map_path=self.map_path,
                                        double_players=self.double_players,
                                        BFS_open=True,
                                    )
                                else:
                                    self.__init__(
                                        screen=self.screen,
                                        map_path=self.map_path,
                                        double_players=self.double_players,
                                        BFS_open=False,
                                    )

                                self.level_cnt = level_cnt_temp  # 恢复关卡计数值
                                self.run()

    def draw(self, current_time):
        # draw the exit popup

        # draw the background
        self.screen.blit(self.background_image, (0, 0))
        # draw brick and iron
        for brick in self.back_ground.brick_group:
            self.screen.blit(brick.image, brick.rect)
        # draw irons
        for iron in self.back_ground.iron_group:
            self.screen.blit(iron.image, iron.rect)
        # draw home
        self.home.draw(self.screen)

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
        if self.BFS_open:
            obstacles = self.get_BFS_map(
                self.all_tank_group,
                self.back_ground.brick_group,
                self.back_ground.iron_group,
            )

        for enemy_tank in self.enemy_tank_group:
            if enemy_tank.flash:
                if self.switch_R1_R2_image:
                    self.screen.blit(
                        enemy_tank.tank_R0,
                        (enemy_tank.rect.left, enemy_tank.rect.top),
                    )
                    if self.enemy_could_move:
                        self.all_tank_group.remove(enemy_tank)
                        if self.BFS_open:
                            enemy_tank.move(
                                self.all_tank_group,
                                self.back_ground.brick_group,
                                self.back_ground.iron_group,
                                obstacles,
                            )
                        else:
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
                        if self.BFS_open:
                            enemy_tank.move(
                                self.all_tank_group,
                                self.back_ground.brick_group,
                                self.back_ground.iron_group,
                                obstacles,
                            )
                        else:
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
                        if enemy_tank.life == 1 or (
                            isinstance(p1_bullet, bullet.Fire_bullet)
                            and enemy_tank.life == 2
                        ):
                            self.score1 += 1
                        enemy_tank.life -= 1
                        if (
                            isinstance(p1_bullet, bullet.Fire_bullet)
                            and enemy_tank.life == 2
                        ):
                            self.damage1 += 2
                        else:
                            self.damage1 += 1

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

                    # if bullet hit home
                    if pygame.sprite.collide_rect(enemy_tank.bullet, self.home):
                        self.home.life = False
                        enemy_tank.bullet.life = False

        if self.game_over or self.home.life == False:
            font = pygame.font.Font(None, 36)
            self.screen.fill((0, 0, 0))
            text = font.render("Game Over!", True, (255, 255, 255))
            text_rect = text.get_rect()
            score1_text = font.render(
                "Number of levels passed by the player: " + str(self.level_cnt),
                True,
                (255, 255, 255),
            )

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

            text = font.render("Press SPACE to play again.", True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (
                self.screen.get_rect().centerx,
                self.screen.get_rect().centery + 40,
            )
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            while self.game_over or self.home.life == False:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.__init__(
                                screen=self.screen,
                                map_path=self.map_path,
                                double_players=self.double_players,
                                BFS_open=self.BFS_open,
                            )
                            self.run()


if __name__ == "__main__":
    try:
        pygame.init()
        screen = pygame.display.set_mode((630, 630))
        pygame.display.set_caption("Tank War")
        tw = Tank_world_Challenge(screen, double_players=False, BFS_open=False)
        tw.run()
    finally:
        pygame.quit()
