import pygame
import sys
import traceback
import ui_class
import map_designer
import bullet_printer
import socket
import threading
import atexit
from tank_world import Tank_world
from net_tank_world import Net_tank_world
from client import Client
from server import Server
from utilise import *


pygame.init()
pygame.mixer.init()

return_button_image = pygame.image.load("../image/return.png")
return_button_image = pygame.transform.scale(return_button_image, (24, 24))
enter_design_button_image = pygame.image.load("../image/enter_map_designer.png")
enter_printer_button_image = pygame.image.load("../image/enter_bullet_printer.png")
setting_return_button_rect = return_button_image.get_rect(topleft=(10, 10))
enter_designer_button_rect = enter_design_button_image.get_rect(topleft=(165, 500))
enter_printer_button_rect = enter_printer_button_image.get_rect(topleft=(165, 350))


button_width = 200
button_height = 100
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((630, 630))

# 初始化ui组件
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

online_game_button = ui_class.Button(
    350,
    480,
    button_width,
    button_height,
    "Online Game",
    font_size=25,
    text_color=WHITE,
    background_color=(30, 30, 220),
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


button_list = [
    single_game_button,
    double_game_button,
    setting_button,
    online_game_button,
]

select_popup = ui_class.Popup(screen, "select player number", "Player 1", "Player 2")
exit_signal = threading.Event()
server_started = False
open_BFS = False


def draw(screen, popup_running=False):
    for button in button_list:
        button.draw(screen)

    if popup_running:
        select_popup.draw()


def run_server(ip, port, exit_signal):
    global server_started
    if server_started:
        return
    server_started = True
    Server(ip, port, exit_signal)


def clean_up(server_thread):
    if server_thread.is_alive():
        server_thread.join()


def main():
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.load("../music/music1.mp3")
    pygame.mixer.music.play(-1)
    pygame.display.set_caption("Tank War Plus")
    tw = Tank_world(screen, double_players=False)
    background = init_ui_background()

    while True:
        screen.blit(background, (0, 0))
        draw(screen, select_popup.running)

        pygame.display.flip()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_signal.set()
                atexit._run_exitfuncs()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if single_game_button.click(event):
                    tw.__init__(screen, double_players=False)
                    tw.run()

                elif double_game_button.click(event):
                    tw.__init__(screen, double_players=True)
                    tw.run()
                elif online_game_button.click(event):
                    select_popup.running = True
                elif select_popup.running and event.type == pygame.MOUSEBUTTONDOWN:
                    if select_popup.button1.click(event):
                        select_popup.running = False
                        server_thread = threading.Thread(
                            target=run_server, args=("0.0.0.0", 8888, exit_signal)
                        )
                        server_thread.start()
                        atexit.register(
                            clean_up,
                            server_thread,
                        )
                        s = socket.socket()
                        s.connect(("192.168.1.153", 8888))
                        client = Client(s, screen)
                        client.send({"protocol": "cli_login", "role_id": 1})
                        print("等待服务器响应")
                        while not g.player:
                            pass
                        print("连接服务器成功")
                        net_tank_world = Net_tank_world(screen, client)
                        net_tank_world.run()
                    if select_popup.button2.click(event):
                        select_popup.running = False
                        s = socket.socket()
                        s.connect(("192.168.1.153", 8888))
                        client = Client(s, screen)
                        client.send({"protocol": "cli_login", "role_id": 2})
                        print("等待服务器响应")
                        while not g.player:
                            pass
                        print("连接服务器成功")
                        net_tank_world = Net_tank_world(screen, client)
                        net_tank_world.run()
                    if select_popup.close_button.click(event):
                        select_popup.running = False
                elif setting_button.click(event):
                    return_flag = True
                    while return_flag:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                mouse_pos = pygame.mouse.get_pos()
                                # 判断是否点击了返回按钮
                                if setting_return_button_rect.collidepoint(mouse_pos):
                                    return_flag = False
                                if enter_designer_button_rect.collidepoint(mouse_pos):
                                    designer_screen = pygame.display.set_mode(
                                        (800, 600)
                                    )
                                    designer = map_designer.Map_designer(
                                        designer_screen
                                    )
                                    pygame.mouse.set_visible(False)
                                    designer.run()
                                    pygame.mouse.set_visible(True)
                                    pygame.display.set_mode((630, 630))
                                if enter_printer_button_rect.collidepoint(mouse_pos):
                                    bullet_printer.main()

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

                        screen.blit(return_button_image, setting_return_button_rect)
                        screen.blit(
                            enter_design_button_image, enter_designer_button_rect
                        )
                        screen.blit(
                            enter_printer_button_image, enter_printer_button_rect
                        )
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
