import pygame
import sys
import wall
import tank
import food
import bullet
import random
import time
from game_global import g

random.seed(1)

client = None  # 客户端Socket
globalV = {}  # 全局通用变量
player_tanks_list = []  # 玩家坦克列表
MAX_PLAYER_NUM = 2  # 最大玩家数量


def game_mode(screen, double_players: bool = False):
    globalV.clear()
    player_tanks_list.clear()
    for i in range(MAX_PLAYER_NUM):
        player_tanks_list.append(None)

    tank.Enemy_tank.tank_id = 0
    moving1 = 0
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
    globalV["all_tank_group"] = all_tank_group
    player_tank_group = pygame.sprite.Group()
    globalV["player_tank_group"] = player_tank_group
    enemy_tank_group = pygame.sprite.Group()
    globalV["enemy_tank_group"] = enemy_tank_group
    enemy_bullet_group = pygame.sprite.Group()
    globalV["enemy_bullet_group"] = enemy_bullet_group

    back_ground = wall.Map()
    globalV["back_ground"] = back_ground
    foods = food.Food()

    font = pygame.font.Font(None, 36)

    player_tank1 = None

    for i in range(MAX_PLAYER_NUM):
        player_tanks_list[i] = tank.Player_tank(i + 1)
        all_tank_group.add(player_tanks_list[i])
        player_tank_group.add(player_tanks_list[i])
        if i + 1 == g.player.role_id:
            player_tank1 = player_tanks_list[i]
            globalV["player_tank1"] = player_tank1

    for i in range(1, 4):
        enemy = tank.Enemy_tank(i, i)
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
    pygame.time.set_timer(DELAYEVENT, 2000)
    # when enemy tank fire, delay 1000ms
    ENEMYBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 1
    pygame.time.set_timer(ENEMYBULLETNOTCOOLINGEVENT, 1500)
    # when player tank fire, delay 200ms
    PLAYERBULLETNOTCOOLINGEVENT = pygame.constants.USEREVENT + 2
    # enemy tank still 8000ms, then move
    NOTMOVEEVENT = pygame.constants.USEREVENT + 3
    pygame.time.set_timer(NOTMOVEEVENT, 8000)

    delay = 100

    score1 = 0
    running_T1 = True
    last_player_shot_time_T1 = 0
    enemy_could_move = True
    switch_R1_R2_image = True
    home_survive = True
    clock = pygame.time.Clock()

    while True:
        current_time = pygame.time.get_ticks()

        if not g.game_start:
            screen.fill((0, 0, 0))
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
                if len(enemy_tank_group) < 3:
                    if g.player.role_id == 1:
                        # 由1号玩家告知服务端有新的敌人出现
                        enemy = tank.Enemy_tank()
                        if not pygame.sprite.spritecollide(
                            enemy, all_tank_group, False, None
                        ):
                            client.send(
                                {
                                    "protocol": "enemy_birth",
                                    "tank_id": tank.Enemy_tank.tank_id,
                                }
                            )
                    # enemy = tank.Enemy_tank()
                    # if pygame.sprite.spritecollide(enemy, all_tank_group, False, None):
                    #     break
                    # all_tank_group.add(enemy)
                    # enemy_tank_group.add(enemy)

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_c and pygame.KMOD_CTRL) or (
                    event.key == pygame.K_ESCAPE
                ):
                    pygame.quit()
                    sys.exit()

        # update the status of player tank
        player_tank_group.update(screen)
        enemy_tank_group.update()
        for enemy_tank in enemy_tank_group:
            if enemy_tank.slow_down:
                if current_time - enemy_tank.slow_down_timer >= 5000:
                    enemy_tank.slow_down = False
        # check player keyboard control
        key_pressed = pygame.key.get_pressed()

        if len(player_tank_group) <= 0 or not g.game_start:
            if enemy_tanks_info:
                # 告知服务端游戏结束
                client.send({"protocol": "game_over"})

        # player 1 control
        if player_tank1.life > 0:
            # if player_tank1.moving1:
            #     player_tank1.moving1 -= 1
            #     all_tank_group.remove(player_tank1)
            #     if player_tank1.move_func(
            #         all_tank_group, back_ground.brick_group, back_ground.iron_group
            #     ):
            #         player_tank1.moving1 += 1
            #     all_tank_group.add(player_tank1)
            #     running_T1 = True

            # if not player_tank1.moving1:

            # 向服务端告知该玩家的操作（如玩家操作上下左右移动）
            if key_pressed[pygame.K_w]:
                client.send(
                    {
                        "protocol": "cli_move",
                        "dir": "up",
                        "x": player_tank1.rect.x,
                        "y": player_tank1.rect.y,
                        "t": current_time,
                    }
                )
            elif key_pressed[pygame.K_s]:
                client.send(
                    {
                        "protocol": "cli_move",
                        "dir": "down",
                        "x": player_tank1.rect.x,
                        "y": player_tank1.rect.y,
                        "t": current_time,
                    }
                )
            elif key_pressed[pygame.K_a]:
                client.send(
                    {
                        "protocol": "cli_move",
                        "dir": "left",
                        "x": player_tank1.rect.x,
                        "y": player_tank1.rect.y,
                        "t": current_time,
                    }
                )
            elif key_pressed[pygame.K_d]:
                client.send(
                    {
                        "protocol": "cli_move",
                        "dir": "right",
                        "x": player_tank1.rect.x,
                        "y": player_tank1.rect.y,
                        "t": current_time,
                    }
                )
            if key_pressed[pygame.K_j]:
                if current_time - last_player_shot_time_T1 >= 500:
                    fire_sound.play()
                    # player_tank1.shoot()
                    # player_tank1.bullet_not_cooling = True
                    last_player_shot_time_T1 = current_time

                    # 告知服务器该玩家坦克发生射击动作
                    client.send({"protocol": "player_shoot"})

        client.send(
            {
                "protocol": "player_pos",
                "dir": player_tank1.direction,
                "left": player_tank1.rect.left,
                "top": player_tank1.rect.top,
            }
        )

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

        # if not (delay % 5):
        #     switch_R1_R2_image = not switch_R1_R2_image

        # show the score

        score_text1 = font.render(f"Your Score: {score1}", True, (255, 255, 255))
        screen.blit(score_text1, (10, 10))

        # draw player tank

        for i in range(MAX_PLAYER_NUM):
            if player_tanks_list[i].life > 0:
                screen.blit(
                    player_tanks_list[i].tank_R0,
                    (player_tanks_list[i].rect.left, player_tanks_list[i].rect.top),
                )
                if pygame.sprite.spritecollide(
                    player_tanks_list[i], back_ground.brick_group, False, None
                ) or pygame.sprite.spritecollide(
                    player_tanks_list[i], back_ground.iron_group, False, None
                ):
                    player_tanks_list[i].moving1 = 0

        player_tank_group.update(screen)

        enemy_tanks_info = {}
        for enemy_tank in enemy_tank_group:
            if enemy_tank.flash:
                screen.blit(
                    enemy_tank.tank_R1, (enemy_tank.rect.left, enemy_tank.rect.top)
                )

                if g.player.role_id == 1:
                    all_tank_group.remove(enemy_tank)
                    enemy_tank.move(
                        all_tank_group,
                        back_ground.brick_group,
                        back_ground.iron_group,
                    )
                    all_tank_group.add(enemy_tank)
                    enemy_tanks_info[enemy_tank.tank_id] = [
                        enemy_tank.direction,
                        enemy_tank.rect.left,
                        enemy_tank.rect.top,
                    ]

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
                    if g.player.role_id == 1:
                        enemy_tanks_info[enemy_tank.tank_id] = [
                            enemy_tank.direction,
                            enemy_tank.rect.left,
                            enemy_tank.rect.top,
                        ]
                    enemy_tank.flash = True
        if g.player.role_id == 1 and enemy_tanks_info:
            # 告知服务端敌人发生移动，仅由1号玩家来告知服务端
            client.send({"protocol": "enemy_move", "info": enemy_tanks_info})

        # draw player 1 bullet

        for i in range(MAX_PLAYER_NUM):
            for p1_bullet in player_tanks_list[i].bullets_list:
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
                            if enemy_tank.life == 1 and (i + 1) == g.player.role_id:
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

        # draw enemy bullet
        for enemy_tank in enemy_tank_group:
            # if enemy bullet not life, then enemy tank shoot
            if g.player.role_id == 1:
                if (
                    not enemy_tank.bullet.life
                    and enemy_tank.bullet_not_cooling
                    and enemy_could_move
                ):
                    # 告知服务端敌人坦克发生射击动作，仅由1号玩家来告知服务端
                    client.send({"protocol": "enemy_shoot"})
                # if the sound is playing, then draw bullet
            if enemy_tank.flash:
                if enemy_tank.bullet.life:
                    # if enemy can move
                    enemy_tank.bullet.move()
                    screen.blit(enemy_tank.bullet.bullet, enemy_tank.bullet.rect)

                    # if bullet hit player tank

                    for i in range(MAX_PLAYER_NUM):
                        if (
                            pygame.sprite.collide_rect(
                                enemy_tank.bullet, player_tanks_list[i]
                            )
                            and player_tanks_list[i] in player_tank_group
                        ):
                            # 告知服务端玩家受到攻击，仅由1号玩家来告知服务端
                            if g.player.role_id == 1:
                                client.send(
                                    {"protocol": "player_injured", "role_id": i + 1}
                                )
                            # 若血量低于 0 ，则告知服务端该玩家已死亡
                            if player_tanks_list[i].life <= 1:
                                client.send(
                                    {"protocol": "player_die", "role_id": i + 1}
                                )
                            # player_tanks_list[i].life -= 1
                            enemy_tank.bullet.life = False
                            bang_sound.play()
                            player_tanks_list[i].moving1 = 0

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

        delay -= 1
        if not delay:
            delay = 100
        pygame.display.flip()
        clock.tick(60)

    if g.game_start and not g.round_start:
        screen.fill((0, 0, 0))
        text = font.render("Game Over!", True, (255, 255, 255))
        text_rect = text.get_rect()
        score1_text = font.render("Your Score: " + str(score1), True, (255, 255, 255))
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

        text = font.render("Player 1 Press space to play again.", True, (255, 255, 255))
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
                    if event.key == pygame.K_SPACE and g.player.role_id == 1:
                        # 由1号玩家告知服务端游戏开始
                        client.send({"protocol": "game_start"})
                        game_mode(screen, double_players=double_players)
            if g.round_start:
                game_mode(screen, double_players=double_players)
