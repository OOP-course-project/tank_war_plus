import os
import sys
import pygame
import traceback
import ui_class
import map_designer
import bullet_printer
import socket
import threading
import atexit
from tank_world import Tank_world
from tank_world_challenge import Tank_world_Challenge
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
enter_printer_button_rect = enter_printer_button_image.get_rect(topleft=(165, 380))


button_width = 200
button_height = 100
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((630, 630))

# 初始化地图下拉菜单, 居中显示
map_dropdown = ui_class.DropdownMenu(
    screen.get_width() / 2 - 100,
    170,
    200,
    50,
    [],
    background_color=(67, 101, 143),
    text_color=WHITE,
)
# 初始化ui组件
music_volume_slider = ui_class.Slider(
    screen,
    length=500,
    initial_position=(250, 100),
    color_line=(67, 101, 143),
    color_button=(35, 35, 35),
    button_radius=10,
)

single_game_button = ui_class.Button(
    493,
    52,
    119,
    83,
    "Single Game",
    font_size=20,
    text_color=WHITE,
    background_color=(26, 26, 26),
    border_color=(92, 16 * 13, 50),
)

double_game_button = ui_class.Button(
    493,
    211,
    119,
    83,
    "Double Game",
    font_size=20,
    text_color=WHITE,
    background_color=(26, 26, 26),
    border_color=(92, 16 * 13, 50),
)

online_game_button = ui_class.Button(
    493,
    370,
    119,
    83,
    "Online Game",
    font_size=20,
    text_color=WHITE,
    background_color=(26, 26, 26),
    border_color=(92, 16 * 13, 50),
)

challenge_game_button = ui_class.Button(
    493,
    529,
    119,
    83,
    "Challenge Mode",
    font_size=20,
    text_color=WHITE,
    background_color=(26, 26, 26),
    border_color=(92, 16 * 13, 50),
)

about_button = ui_class.Button(
    screen.get_width() / 2 - 60,
    565,
    120,
    37,
    "About",
    font_size=20,
    text_color=WHITE,
    background_color=(26, 26, 26),
    border_color=(92, 16 * 13, 50),
)

setting_button = ui_class.RoundedRectangleButton(
    50,
    527,
    140,
    85,
    10,
    "Settings",
    font_size=20,
    text_color=WHITE,
    background_color=(40, 40, 40),
    border_color=(92, 16 * 13, 50),
)

text_box_font = pygame.font.Font("../fonts/FiraCode-Medium.ttf", 20)
ip_textbox = ui_class.TextInputBox(
    screen, screen.get_rect().centerx - 50, 250, 200, 30, text_box_font
)
port_textbox = ui_class.TextInputBox(
    screen, screen.get_rect().centerx - 50, 300, 200, 30, text_box_font
)


button_list = [
    single_game_button,
    double_game_button,
    setting_button,
    challenge_game_button,
    about_button,
    online_game_button,
]

select_popup = ui_class.Popup(screen, "select player number", "Player 1", "Player 2")
exit_signal = threading.Event()
server_started = False
BFS_open = True
server_IP = "192.168.1.153"
server_port = 8888


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
    pygame.display.set_icon(pygame.image.load("../image/icon.png"))
    now_map_path = "../maps/initial_points.json"
    global server_IP, server_port, BFS_open, server_started, screen

    tw = Tank_world(
        screen,
        map_path=now_map_path,
        double_players=False,
        BFS_open=BFS_open,
    )

    tw_challenge = Tank_world_Challenge(
        screen,
        map_path=now_map_path,
        double_players=False,
        BFS_open=BFS_open,
    )

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
                    tw.__init__(
                        screen,
                        map_path=now_map_path,
                        double_players=False,
                        BFS_open=BFS_open,
                    )
                    tw.run()

                elif double_game_button.click(event):
                    tw.__init__(
                        screen,
                        map_path=now_map_path,
                        double_players=True,
                        BFS_open=BFS_open,
                    )
                    tw.run()
                elif online_game_button.click(event):
                    select_popup.running = True
                elif challenge_game_button.click(event):
                    tw_challenge.__init__(
                        screen,
                        map_path=now_map_path,
                        double_players=False,
                        BFS_open=False,
                    )
                    tw_challenge.run()
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
                        s.connect((server_IP, server_port))
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
                        s.connect((server_IP, server_port))
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
                elif about_button.click(event):
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
                        screen.fill((200, 200, 200))
                        # 写出制作组成员名字
                        font = pygame.font.Font(None, 30)
                        text1 = font.render("Developer", True, (0, 0, 0))
                        text1_rect = text1.get_rect()
                        text1_rect.centerx = screen.get_rect().centerx
                        text1_rect.centery = 70
                        text2 = font.render("Zilyu Ye", True, (0, 0, 0))
                        text2_rect = text2.get_rect()
                        text2_rect.centerx = screen.get_rect().centerx
                        text2_rect.centery = 140
                        text3 = font.render("Enhua Zhang", True, (0, 0, 0))
                        text3_rect = text3.get_rect()
                        text3_rect.centerx = screen.get_rect().centerx
                        text3_rect.centery = 210
                        text4 = font.render("Chengkai Wang", True, (0, 0, 0))
                        text4_rect = text4.get_rect()
                        text4_rect.centerx = screen.get_rect().centerx
                        text4_rect.centery = 280
                        text5 = font.render("Runze Fang", True, (0, 0, 0))
                        text5_rect = text5.get_rect()
                        text5_rect.centerx = screen.get_rect().centerx
                        text5_rect.centery = 350
                        # 绘制名字和返回按钮

                        screen.blit(text1, text1_rect)
                        screen.blit(text2, text2_rect)
                        screen.blit(text3, text3_rect)
                        screen.blit(text4, text4_rect)
                        screen.blit(text5, text5_rect)
                        screen.blit(return_button_image, setting_return_button_rect)

                        pygame.display.flip()

                elif setting_button.click(event):
                    return_flag = True

                    map_list = os.listdir("../maps")
                    map_dropdown.options = map_list
                    if map_dropdown.get_now_option() is None:
                        map_dropdown.selected_option = map_list[0]
                    map_dropdown.selected_option = map_dropdown.get_now_option()
                    while return_flag:
                        now_map_path = os.path.join(
                            "../maps", map_dropdown.get_now_option()
                        )
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                mouse_pos = pygame.mouse.get_pos()
                                # 判断是否点击了返回按钮
                                if setting_return_button_rect.collidepoint(mouse_pos):
                                    server_IP = ip_textbox.get_text()
                                    if port_textbox.get_text().isdigit():
                                        server_port = int(port_textbox.get_text())
                                    return_flag = False
                                if enter_designer_button_rect.collidepoint(mouse_pos):
                                    designer_screen = pygame.display.set_mode(
                                        (824, 624)
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
                            map_dropdown.handle_event(event)
                            ip_textbox.handle_event(event)
                            port_textbox.handle_event(event)

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

                        screen.fill((200, 200, 200))
                        # 在滑块正上方写出音量调节
                        font = pygame.font.Font(None, 30)
                        text1 = font.render("Music Volume", True, (0, 0, 0))
                        text1_rect = text1.get_rect()
                        text1_rect.centerx = screen.get_rect().centerx
                        text1_rect.centery = 70
                        # 在滑块正下方写出地图选择
                        text2 = font.render("Map Selection", True, (0, 0, 0))
                        text2_rect = text2.get_rect()
                        text2_rect.centerx = screen.get_rect().centerx
                        text2_rect.centery = 140
                        # 在第一个文本框左边写出服务器IP
                        text3 = font.render("Server IP", True, (0, 0, 0))
                        text3_rect = text3.get_rect()
                        text3_rect.centerx = screen.get_rect().centerx - 130
                        text3_rect.centery = 270
                        # 在第二个文本框左边写出服务器端口
                        text4 = font.render("Server Port", True, (0, 0, 0))
                        text4_rect = text4.get_rect()
                        text4_rect.centerx = screen.get_rect().centerx - 130
                        text4_rect.centery = 320

                        music_volume_slider.draw()
                        map_dropdown.draw(screen)
                        ip_textbox.draw()
                        port_textbox.draw()

                        screen.blit(text1, text1_rect)
                        screen.blit(text2, text2_rect)
                        screen.blit(text3, text3_rect)
                        screen.blit(text4, text4_rect)
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
