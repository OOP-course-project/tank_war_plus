import pygame
import sys
import wall
import tank
import food
import bullet

def game_mode(screen, double_players: bool = False):
    background_image = pygame.image.load(r"../image/background.png").convert_alpha()
    home_image = pygame.image.load(r"../image/home.png").convert_alpha()
    home_destroyed_image = pygame.image.load(
        r"../image/home_destroyed.png"
    ).convert_alpha()
    bang_sound = pygame.mixer.Sound(r"../music/bang.wav")
    fire_sound = pygame.mixer.Sound(r"../music/Gunfire.wav")
    start_sound = pygame.mixer.Sound(r"../music/start.wav")
    enemy_appear = pygame.image.load(r"../image/appear.png").convert_alpha()
    bang_sound.set_volume(1)
    start_sound.play()

    all_tank_group = pygame.sprite.Group()
    player_tank_group = pygame.sprite.Group()
    enemy_tank_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()

    back_ground = wall.Map()
    foods = food.Food()

    player_tank1 = tank.Player_tank(1)
    all_tank_group.add(player_tank1)
    player_tank_group.add(player_tank1)

    if double_players:
        player_tank2 = tank.Player_tank(2)
        all_tank_group.add(player_tank2)
        player_tank_group.add(player_tank2)

    for i in range(1, 4):
        enemy = tank.Enemy_tank(i)
        all_tank_group.add(enemy)
        enemy_tank_group.add(enemy)

    # enemy tank appearance image
    appearance = []
    appearance.append(enemy_appear.subsurface((0, 0), (48, 48)))
    appearance.append(enemy_appear.subsurface((48, 0), (48, 48)))
    appearance.append(enemy_appear.subsurface((96, 0), (48, 48)))

    # custom event
    # when create enemy tank, delay 200ms
    DELAYEVENT = pygame.constants.USEREVENT
    pygame.time.set_timer(DELAYEVENT, 200)
    # when enemy tank fire, delay 1000ms
    ENEMYBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 1
    pygame.time.set_timer(ENEMYBULLETNOTCOOLINGEVENT, 1000)
    # when player tank fire, delay 200ms
    PLAYERBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 2
    # enemy tank still 8000ms, then move
    NOTMOVEEVENT = pygame.constants.USEREVENT + 3
    pygame.time.set_timer(NOTMOVEEVENT, 8000)

    # judge if the game is over
    game_over = False

    delay = 100
    moving1 = 0
    score1 = 0
    running_T1 = True
    move_direction1 = "up"
    last_player_shot_time_T1 = 0
    if double_players:
        moving2 = 0
        score2 = 0
        move_direction2 = "up"
        running_T2 = True
        last_player_shot_time_T2 = 0
    enemy_could_move = True
    switch_R1_R2_image = True
    home_survive = True
    clock = pygame.time.Clock()
    while not game_over:
        print(moving1)
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == PLAYERBULLETNOTCOOLINGEVENT:
                # player tank bullet cooling 0.5s
                if current_time - last_player_shot_time_T1 >= 500:
                    player_tank1.bullet_not_cooling = True
                if current_time - last_player_shot_time_T2 >= 500:
                    player_tank2.bullet_not_cooling = True

            if event.type == ENEMYBULLETNOTCOOLINGEVENT:
                for enemy in enemy_tank_group:
                    enemy.bullet_not_cooling = True

            if event.type == NOTMOVEEVENT:
                enemy_could_move = True

            if event.type == DELAYEVENT:
                if len(enemy_tank_group) < 4:
                    enemy = tank.Enemy_tank()
                    if pygame.sprite.spritecollide(enemy, all_tank_group, False, None):
                        break
                    all_tank_group.add(enemy)
                    enemy_tank_group.add(enemy)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and pygame.KMOD_CTRL:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_1:
                    for x, y in [
                        (11, 23),
                        (12, 23),
                        (13, 23),
                        (14, 23),
                        (11, 24),
                        (14, 24),
                        (11, 25),
                        (14, 25),
                    ]:
                        back_ground.brick = wall.Brick()
                        back_ground.brick.rect.left, back_ground.brick.rect.top = (
                            3 + x * 24,
                            3 + y * 24,
                        )
                        back_ground.brick_group.add(back_ground.brick)
                if event.key == pygame.K_4:
                    for x, y in [
                        (11, 23),
                        (12, 23),
                        (13, 23),
                        (14, 23),
                        (11, 24),
                        (14, 24),
                        (11, 25),
                        (14, 25),
                    ]:
                        back_ground.iron = wall.Iron()
                        back_ground.iron.rect.left, back_ground.iron.rect.top = (
                            3 + x * 24,
                            3 + y * 24,
                        )
                        back_ground.iron_group.add(back_ground.iron)

        # update the status of player tank
        player_tank_group.update(screen)
        enemy_tank_group.update()
        for enemy_tank in enemy_tank_group:
            if enemy_tank.slow_down:
                if current_time - enemy_tank.slow_down_timer >= 5000:
                    enemy_tank.slow_down = False
        # check player keyboard control
        key_pressed = pygame.key.get_pressed()

        if len(player_tank_group) <= 0:
            game_over = True

        # player 1 control
        if player_tank1.life > 0:
            if moving1:
                moving1 -= 1
                all_tank_group.remove(player_tank1)
                if player_tank1.move_func(
                    all_tank_group, back_ground.brick_group, back_ground.iron_group
                ):
                    moving1 += 1
                all_tank_group.add(player_tank1)
                running_T1 = True
            if not moving1:
                if key_pressed[pygame.K_w]:
                    moving1 = 7
                    move_direction1 = "up"
                    player_tank1.direction = "up"
                    running_T1 = True
                    all_tank_group.remove(player_tank1)
                    if player_tank1.move_func(
                        all_tank_group, back_ground.brick_group, back_ground.iron_group
                    ):
                        moving1 = 0
                    all_tank_group.add(player_tank1)
                elif key_pressed[pygame.K_s]:
                    moving1 = 7
                    move_direction1 = "down"
                    player_tank1.direction = "down"
                    running_T1 = True
                    all_tank_group.remove(player_tank1)
                    if player_tank1.move_func(
                        all_tank_group, back_ground.brick_group, back_ground.iron_group
                    ):
                        moving1 = 0
                    all_tank_group.add(player_tank1)
                elif key_pressed[pygame.K_a]:
                    moving1 = 7
                    move_direction1 = "left"
                    player_tank1.direction = "left"
                    running_T1 = True
                    all_tank_group.remove(player_tank1)
                    if player_tank1.move_func(
                        all_tank_group, back_ground.brick_group, back_ground.iron_group
                    ):
                        moving1 = 0
                    all_tank_group.add(player_tank1)
                elif key_pressed[pygame.K_d]:
                    moving1 = 7
                    move_direction1 = "right"
                    player_tank1.direction = "right"
                    running_T1 = True
                    all_tank_group.remove(player_tank1)
                    if player_tank1.move_func(
                        all_tank_group, back_ground.brick_group, back_ground.iron_group
                    ):
                        moving1 = 0
                    all_tank_group.add(player_tank1)
            if key_pressed[pygame.K_j]:
                if current_time - last_player_shot_time_T1 >= 500:
                    fire_sound.play()
                    player_tank1.shoot()
                    player_tank1.bullet_not_cooling = True
                    last_player_shot_time_T1 = current_time

        if double_players:
            if player_tank2.life > 0:
                # player 2 moving
                if moving2:
                    moving2 -= 1
                    all_tank_group.remove(player_tank2)
                    if player_tank2.move_func(
                        all_tank_group, back_ground.brick_group, back_ground.iron_group
                    ):
                        moving2 += 1
                    all_tank_group.add(player_tank2)
                    running_T2 = True
                else:
                    if key_pressed[pygame.K_UP]:
                        moving2 = 7
                        move_direction2 = "up"
                        player_tank2.direction = "up"
                        all_tank_group.remove(player_tank2)
                        if player_tank2.move_func(
                            all_tank_group,
                            back_ground.brick_group,
                            back_ground.iron_group,
                        ):
                            moving2 = 0
                        all_tank_group.add(player_tank2)
                    elif key_pressed[pygame.K_DOWN]:
                        moving2 = 7
                        move_direction2 = "down"
                        player_tank2.direction = "down"
                        all_tank_group.remove(player_tank2)
                        if player_tank2.move_func(
                            all_tank_group,
                            back_ground.brick_group,
                            back_ground.iron_group,
                        ):
                            moving2 = 0
                        all_tank_group.add(player_tank2)
                    elif key_pressed[pygame.K_LEFT]:
                        moving2 = 7
                        move_direction2 = "left"
                        player_tank2.direction = "left"
                        all_tank_group.remove(player_tank2)
                        if player_tank2.move_func(
                            all_tank_group,
                            back_ground.brick_group,
                            back_ground.iron_group,
                        ):
                            moving2 = 0
                        all_tank_group.add(player_tank2)
                    elif key_pressed[pygame.K_RIGHT]:
                        moving2 = 7
                        move_direction2 = "right"
                        player_tank2.direction = "right"
                        all_tank_group.remove(player_tank2)
                        if player_tank2.move_func(
                            all_tank_group,
                            back_ground.brick_group,
                            back_ground.iron_group,
                        ):
                            moving2 = 0
                        all_tank_group.add(player_tank2)
                if key_pressed[pygame.K_KP0]:
                    if current_time - last_player_shot_time_T2 >= 500:
                        fire_sound.play()
                        player_tank2.shoot()
                        player_tank2.bullet_not_cooling = True
                        last_player_shot_time_T2 = current_time

        # draw background
        screen.blit(background_image, (0, 0))
        # draw bricks
        for brick in back_ground.brick_group:
            screen.blit(brick.image, brick.rect)
        # draw irons
        for iron in back_ground.iron_group:
            screen.blit(iron.image, iron.rect)
        # draw home
        if home_survive:
            screen.blit(home_image, (3 + 24 * 12, 3 + 24 * 24))
        else:
            screen.blit(home_destroyed_image, (3 + 24 * 12, 3 + 24 * 24))

        if not (delay % 5):
            switch_R1_R2_image = not switch_R1_R2_image

        # show the score
        font = pygame.font.Font(None, 36)
        score_text1 = font.render(f"Score1: {score1}", True, (255, 255, 255))
        screen.blit(score_text1, (10, 10))
        if double_players:
            score_text2 = font.render(f"Score2: {score2}", True, (255, 255, 255))
            screen.blit(
                score_text2, (screen.get_width() - score_text2.get_width() - 10, 10)
            )

        # draw player tank
        if player_tank1.life > 0:
            if switch_R1_R2_image and running_T1:
                screen.blit(
                    player_tank1.tank_R1,
                    (player_tank1.rect.left, player_tank1.rect.top),
                )
                running_T1 = False
            else:
                screen.blit(
                    player_tank1.tank_R0,
                    (player_tank1.rect.left, player_tank1.rect.top),
                )
            if pygame.sprite.spritecollide(
                player_tank1, back_ground.brick_group, False, None
            ) or pygame.sprite.spritecollide(
                player_tank1, back_ground.iron_group, False, None
            ):
                moving1 = 0
        if double_players:
            if player_tank2.life > 0:
                if switch_R1_R2_image and running_T2:
                    screen.blit(
                        player_tank2.tank_R0,
                        (player_tank2.rect.left, player_tank2.rect.top),
                    )
                    running_T2 = False
                else:
                    screen.blit(
                        player_tank2.tank_R1,
                        (player_tank2.rect.left, player_tank2.rect.top),
                    )

            if double_players:
                if pygame.sprite.spritecollide(
                    player_tank2, back_ground.brick_group, False, None
                ) or pygame.sprite.spritecollide(
                    player_tank2, back_ground.iron_group, False, None
                ):
                    moving2 = 0

        for enemy_tank in enemy_tank_group:
            if enemy_tank.flash:
                if switch_R1_R2_image:
                    screen.blit(
                        enemy_tank.tank_R0, (enemy_tank.rect.left, enemy_tank.rect.top)
                    )
                    if enemy_could_move:
                        all_tank_group.remove(enemy_tank)
                        enemy_tank.move(
                            all_tank_group,
                            back_ground.brick_group,
                            back_ground.iron_group,
                        )
                        all_tank_group.add(enemy_tank)
                else:
                    screen.blit(
                        enemy_tank.tank_R1, (enemy_tank.rect.left, enemy_tank.rect.top)
                    )
                    if enemy_could_move:
                        all_tank_group.remove(enemy_tank)
                        enemy_tank.move(
                            all_tank_group,
                            back_ground.brick_group,
                            back_ground.iron_group,
                        )
                        all_tank_group.add(enemy_tank)
            else:
                # show the enemy tank appearance
                if enemy_tank.times > 0:
                    enemy_tank.times -= 1
                    if enemy_tank.times <= 10:
                        screen.blit(appearance[2], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 20:
                        screen.blit(appearance[1], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 30:
                        screen.blit(appearance[0], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 40:
                        screen.blit(appearance[2], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 50:
                        screen.blit(appearance[1], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 60:
                        screen.blit(appearance[0], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 70:
                        screen.blit(appearance[2], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 80:
                        screen.blit(appearance[1], (3 + enemy_tank.x * 12 * 24, 3))
                    elif enemy_tank.times <= 90:
                        screen.blit(appearance[0], (3 + enemy_tank.x * 12 * 24, 3))
                if enemy_tank.times == 0:
                    enemy_tank.flash = True

        player_tank_group.update(screen)
        # draw player 1 bullet
        for p1_bullet in player_tank1.bullets_list:
            if p1_bullet.life:
                p1_bullet.move()
                screen.blit(p1_bullet.bullet, p1_bullet.rect)

                # bullet hit enemy bullet
                for enemy_bullet in enemy_bullet_group:
                    if enemy_bullet.life:
                        if pygame.sprite.collide_rect(p1_bullet, enemy_bullet):
                            p1_bullet.life = False
                            enemy_bullet.life = False
                            pygame.sprite.spritecollide(
                                p1_bullet, enemy_bullet_group, True, None
                            )

                # bullet hit enemy tank
                for enemy_tank in enemy_tank_group:
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
                        bang_sound.play()
                        p1_bullet.life = False
                        p1_bullet.kill()
                        if enemy_tank.life == 1:
                            score1 += 1
                        enemy_tank.life -= 1

                # bullet hit brick
                if pygame.sprite.spritecollide(
                    p1_bullet, back_ground.brick_group, True, None
                ):
                    p1_bullet.life = False
                    p1_bullet.rect.left, p1_bullet.rect.top = (
                        3 + 12 * 24,
                        3 + 24 * 24,
                    )

                # bullet hit iron
                if pygame.sprite.spritecollide(
                    p1_bullet, back_ground.iron_group, False, None
                ):
                    p1_bullet.life = False
                    p1_bullet.rect.left, p1_bullet.rect.top = (
                        3 + 12 * 24,
                        3 + 24 * 24,
                    )

                # bullet hit iron
                if pygame.sprite.spritecollide(
                    p1_bullet, back_ground.iron_group, False, None
                ):
                    p1_bullet.life = False
                    p1_bullet.rect.left, p1_bullet.rect.top = (
                        3 + 12 * 24,
                        3 + 24 * 24,
                    )
        if double_players:
            for p2_bullet in player_tank2.bullets_list:
                if p2_bullet.life:
                    p2_bullet.move()
                    screen.blit(p2_bullet.bullet, p2_bullet.rect)

                    # bullet hit enemy bullet
                    for enemy_bullet in enemy_bullet_group:
                        if enemy_bullet.life:
                            if pygame.sprite.collide_rect(p2_bullet, enemy_bullet):
                                p2_bullet.life = False
                                enemy_bullet.life = False
                                pygame.sprite.spritecollide(
                                    p2_bullet, enemy_bullet_group, True, None
                                )

                    # bullet hit enemy tank
                    for enemy_tank in enemy_tank_group:
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
                            bang_sound.play()
                            p2_bullet.life = False
                            p2_bullet.kill()
                            if enemy_tank.life == 1:
                                score2 += 1
                            enemy_tank.life -= 1

                    # bullet hit brick
                    if pygame.sprite.spritecollide(
                        p2_bullet, back_ground.brick_group, True, None
                    ):
                        p2_bullet.life = False
                        p2_bullet.rect.left, p2_bullet.rect.top = (
                            3 + 12 * 24,
                            3 + 24 * 24,
                        )

                    # bullet hit iron
                    if pygame.sprite.spritecollide(
                        p2_bullet, back_ground.iron_group, False, None
                    ):
                        p2_bullet.life = False
                        p2_bullet.rect.left, p2_bullet.rect.top = (
                            3 + 12 * 24,
                            3 + 24 * 24,
                        )

        # draw enemy bullet
        for enemy_tank in enemy_tank_group:
            # if enemy bullet not life, then enemy tank shoot
            if (
                not enemy_tank.bullet.life
                and enemy_tank.bullet_not_cooling
                and enemy_could_move
            ):
                enemy_bullet_group.remove(enemy_tank.bullet)
                enemy_tank.shoot()
                enemy_bullet_group.add(enemy_tank.bullet)
                enemy_tank.bullet_not_cooling = False
            # if the sound is playing, then draw bullet
            if enemy_tank.flash:
                if enemy_tank.bullet.life:
                    # if enemy can move
                    if enemy_could_move:
                        enemy_tank.bullet.move()
                    screen.blit(enemy_tank.bullet.bullet, enemy_tank.bullet.rect)

                    # if bullet hit player tank
                    if (
                        pygame.sprite.collide_rect(enemy_tank.bullet, player_tank1)
                        and player_tank1 in player_tank_group
                    ):
                        player_tank1.life -= 1
                        enemy_tank.bullet.life = False
                        bang_sound.play()
                        moving1 = 0
                    if double_players:
                        if (
                            pygame.sprite.collide_rect(enemy_tank.bullet, player_tank2)
                            and player_tank2 in player_tank_group
                        ):
                            player_tank2.life -= 1
                            enemy_tank.bullet.life = False
                            bang_sound.play()
                            moving2 = 0

                    # if bullet hit brick
                    if pygame.sprite.spritecollide(
                        enemy_tank.bullet, back_ground.brick_group, True, None
                    ):
                        enemy_tank.bullet.life = False
                    # if bullet hit iron
                    if enemy_tank.bullet.strong:
                        if pygame.sprite.spritecollide(
                            enemy_tank.bullet, back_ground.iron_group, True, None
                        ):
                            enemy_tank.bullet.life = False
                    else:
                        if pygame.sprite.spritecollide(
                            enemy_tank.bullet, back_ground.iron_group, False, None
                        ):
                            enemy_tank.bullet.life = False
        # # draw foods
        # if foods.life:
        #     screen.blit(foods.image, foods.rect)
        #     # player tank eat food

        delay -= 1

        if not delay:
            delay = 100

        pygame.display.flip()
        clock.tick(60)

    if game_over:
        screen.fill((0, 0, 0))
        text = font.render("Game Over!", True, (255, 255, 255))
        text_rect = text.get_rect()
        score1_text = font.render(
            "Player 1 Score: " + str(score1), True, (255, 255, 255)
        )
        if not double_players:
            text_rect.center = (
                screen.get_rect().centerx,
                screen.get_rect().centery,
            )
            screen.blit(text, text_rect)
            score_rect = score1_text.get_rect()
            score_rect.center = (
                screen.get_rect().centerx,
                screen.get_rect().centery + 20,
            )
            screen.blit(score1_text, score_rect)
        if double_players:
            text_rect.center = (
                screen.get_rect().centerx,
                screen.get_rect().centery - 20,
            )
            screen.blit(text, text_rect)
            score2_text = font.render(
                "Player 2 Score: " + str(score2), True, (255, 255, 255)
            )
            score1_rect = score1_text.get_rect()
            score2_rect = score2_text.get_rect()
            score1_rect.center = (
                screen.get_rect().centerx,
                screen.get_rect().centery,
            )
            score2_rect.center = (
                screen.get_rect().centerx,
                screen.get_rect().centery + 20,
            )
            screen.blit(score1_text, score1_rect)
            screen.blit(score2_text, score2_rect)

        text = font.render("Press space to play again.", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen.get_rect().centerx, screen.get_rect().centery + 40)
        screen.blit(text, text_rect)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_mode(screen, double_players=double_players)
