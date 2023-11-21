import pygame
import sys
import wall
import tank
import food


def single_player_test(screen):
    background_image = pygame.image.load(r"../image/background.png").convert_alpha()
    home_image = pygame.image.load(r"../image/home.png").convert_alpha()
    home_destroyed_image = pygame.image.load(
        r"../image/home_destroyed.png"
    ).convert_alpha()
    bang_sound = pygame.mixer.Sound(r"../music/bang.wav")
    fire_sound = pygame.mixer.Sound(r"../music/Gunfire.wav")
    start_sound = pygame.mixer.Sound(r"../music/start.wav")
    enemy_appear = pygame.image.load("../image/appear.png").convert_alpha()
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

    # Mr.Kai, don't die
    game_over = False

    delay = 100
    moving1 = 0
    score1 = 0
    move_direction1 = "up"
    enemy_number = 3
    enemy_could_move = True
    switch_R1_R2_image = True
    home_survive = True
    running_T1 = True
    last_player_shot_time_T1 = 0
    clock = pygame.time.Clock()
    while not game_over:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == PLAYERBULLETNOTCOOLINGEVENT:
                # player tank bullet cooling 0.5s
                if current_time - last_player_shot_time_T1 >= 500:
                    player_tank1.bullet_not_cooling = True

            if event.type == ENEMYBULLETNOTCOOLINGEVENT:
                for enemy in enemy_tank_group:
                    enemy.bullet_not_cooling = True

            if event.type == NOTMOVEEVENT:
                enemy_could_move = True

            if event.type == DELAYEVENT:
                if enemy_number < 4:
                    enemy = tank.Enemy_tank()
                    if pygame.sprite.spritecollide(enemy, all_tank_group, False, None):
                        break
                    all_tank_group.add(enemy)
                    enemy_tank_group.add(enemy)
                    enemy_number += 1

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
        # check player keyboard control
        key_pressed = pygame.key.get_pressed()

        if len(player_tank_group) <= 0:
            pass

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
        else:
            game_over = True

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
        score_text = font.render(f"Score1: {score1}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

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
        if player_tank1.bullet.life:
            player_tank1.bullet.move()
            screen.blit(player_tank1.bullet.bullet, player_tank1.bullet.rect)

            # bullet hit enemy bullet
            for enemy_bullet in enemy_bullet_group:
                if enemy_bullet.life:
                    if pygame.sprite.collide_rect(player_tank1.bullet, enemy_bullet):
                        player_tank1.bullet.life = False
                        enemy_bullet.life = False
                        pygame.sprite.spritecollide(
                            player_tank1.bullet, enemy_bullet_group, True, None
                        )

            # bullet hit enemy tank
            if pygame.sprite.spritecollide(
                player_tank1.bullet, enemy_tank_group, True, None
            ):
                bang_sound.play()
                enemy_number -= 1
                score1 += 1
                player_tank1.bullet.life = False

            # bullet hit brick
            if pygame.sprite.spritecollide(
                player_tank1.bullet, back_ground.brick_group, True, None
            ):
                player_tank1.bullet.life = False
                player_tank1.bullet.rect.left, player_tank1.bullet.rect.top = (
                    3 + 12 * 24,
                    3 + 24 * 24,
                )

            # bullet hit iron
            if pygame.sprite.spritecollide(
                player_tank1.bullet, back_ground.iron_group, False, None
            ):
                player_tank1.bullet.life = False
                player_tank1.bullet.rect.left, player_tank1.bullet.rect.top = (
                    3 + 12 * 24,
                    3 + 24 * 24,
                )

            # bullet hit iron
            if pygame.sprite.spritecollide(
                player_tank1.bullet, back_ground.iron_group, False, None
            ):
                player_tank1.bullet.life = False
                player_tank1.bullet.rect.left, player_tank1.bullet.rect.top = (
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
        
    # Mr.Kai, why do you die so tragically? Whatever, enter the wheel of reincarnation.
    if game_over:

        screen.fill((0, 0, 0))
        text = font.render("Game Over!", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen.get_rect().centerx, screen.get_rect().centery)
        screen.blit(text, text_rect)

        score_text = font.render("Score: " + str(score1), True, (255, 255, 255))
        score_rect = score_text.get_rect()
        score_rect.center = (screen.get_rect().centerx, screen.get_rect().centery + 20)
        screen.blit(score_text, score_rect)

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
                        single_player_test(screen)


