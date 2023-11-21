import pygame
import sys
import single_game_test

def run_game():
    pygame.init()
    pygame.mixer.init()

    resolution = 630, 630
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Tank War")

    # 加载游戏资源
    background_image = pygame.image.load("../image/background_opening.jfif").convert_alpha()
    start_button_image = pygame.image.load("../image/start_button.jpg").convert_alpha()
    exit_button_image = pygame.image.load("../image/exit.jpg").convert_alpha()

    # 设置按钮位置
    button_size = start_button_image.get_size()
    start_button_pos = (resolution[0] // 2 - button_size[0] // 2, 150)
    exit_button_pos = (resolution[0] // 2 - button_size[0] // 2, 450)

    running = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_pos[0] <= mouse_pos[0] <= start_button_pos[0] + button_size[0] and \
                        start_button_pos[1] <= mouse_pos[1] <= start_button_pos[1] + button_size[1]:
                    running = True
                elif exit_button_pos[0] <= mouse_pos[0] <= exit_button_pos[0] + button_size[0] and \
                        exit_button_pos[1] <= mouse_pos[1] <= exit_button_pos[1] + button_size[1]:
                    pygame.quit()
                    sys.exit()

        if running:
            # 在这里调用你的游戏逻辑函数，比如 main()
            single_game_test.single_player_test(screen)
            # 游戏逻辑结束后将 running 重新设置为 False
            running = False

        screen.blit(background_image, (0, 0))
        screen.blit(start_button_image, start_button_pos)
        screen.blit(exit_button_image, exit_button_pos)

        pygame.display.flip()
        clock.tick(60)

# UI部分
def main_ui():
    pygame.init()

    resolution = 800, 600
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Tank War")

    # 加载标题和开发者名单
    title_font = pygame.font.Font(None, 48)
    developer_font = pygame.font.Font(None, 24)
    title_text = title_font.render("Tank War", True, (255, 255, 255))
    developer_text = developer_font.render("Developed by Your Name", True, (255, 255, 255))

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                run_game()

        screen.fill((0, 0, 0))
        screen.blit(title_text, (resolution[0] // 2 - title_text.get_width() // 2, 200))
        screen.blit(developer_text, (resolution[0] // 2 - developer_text.get_width() // 2, 300))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_ui()