import pygame
import sys
import traceback
import wall
import tank
import food
import ui_class
from tank_world import Tank_world
from utilise import *


return_button_image = pygame.image.load("../image/return.png")
return_button_image = pygame.transform.scale(return_button_image, (24, 24))
return_button_rect = return_button_image.get_rect(topleft=(10, 10))
screen = init_pygame((630, 630))
button_width = 200
button_height = 100
WHITE = (255, 255, 255)


music_volume_slider = ui_class.Slider(
    screen,
    length=500,
    initial_position=(250, 100),
    color_line=(0, 0, 255),
    color_button=(0, 255, 0),
    button_radius=10,
)

single_game_button = ui_class.Button(
    350,
    120,
    button_width,
    button_height,
    "Single Game",
    font_size=25,
    text_color=WHITE,
    background_color=(220, 20, 20),
)

double_game_button = ui_class.Button(
    350,
    300,
    button_width,
    button_height,
    "Double Game",
    font_size=25,
    text_color=WHITE,
    background_color=(30, 220, 30),
)

setting_button = ui_class.Button(
    0,
    400,
    button_width,
    button_height,
    "Settings",
    font_size=25,
    text_color=WHITE,
    background_color=(210, 180, 140),
)


def main():
    initial_volume = 0.5
    pygame.mixer.music.set_volume(initial_volume)
    pygame.mixer.music.load("../music/music1.mp3")
    pygame.mixer.music.play(-1)
    pygame.display.set_caption("Tank War Plus")
    background = init_ui_background()
    button_list = [single_game_button, double_game_button, setting_button]

    while True:
        screen.blit(background, (0, 0))
        for button in button_list:
            button.draw(screen)

        pygame.display.flip()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if single_game_button.click(event):
                    tw = Tank_world(screen, double_players=False)
                    tw.run()
                elif double_game_button.click(event):
                    tw = Tank_world(screen, double_players=True)
                    tw.run()
                elif setting_button.click(event):
                    return_flag = True
                    while return_flag:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if (
                                event.type == pygame.MOUSEBUTTONDOWN
                                and event.button == 1
                            ):
                                mouse_pos = pygame.mouse.get_pos()
                                # 判断是否点击了返回按钮
                                if return_button_rect.collidepoint(mouse_pos):
                                    return_flag = False

                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        # 检测鼠标点击事件
                        if pygame.mouse.get_pressed()[0]:  # 左键点击
                            # 更新滑块位置
                            if (50 <= mouse_x <= 550) and (
                                (
                                    music_volume_slider.position[1]
                                    - music_volume_slider.button_radius
                                )
                                <= mouse_y
                                <= (
                                    music_volume_slider.position[1]
                                    + music_volume_slider.button_radius
                                )
                            ):  # 确保在轨道范围内
                                music_volume_slider.update_position((mouse_x, 100))
                                # 计算音量百分比
                                music_volume_percentage = (mouse_x - 50) / 500
                                # 设置音量
                                pygame.mixer.music.set_volume(music_volume_percentage)

                        screen.fill((255, 255, 255))
                        music_volume_slider.draw()
                        screen.blit(return_button_image, return_button_rect)
                        pygame.display.flip()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
