import pygame
import sys
import traceback
import wall
import tank
import food
import game_mode
from game_global import g

from client import Client
import socket

IP_ADDR = '10.37.194.74' # 服务器IP地址
PORT = 8888 # 服务器端口

def main(argv):
    pygame.init()
    pygame.mixer.init()
    resolution = 630, 630
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Tank War")

    # 游戏连接到服务器
    s = socket.socket()
    s.connect((IP_ADDR, PORT))
    client = Client(s, screen)

    # 客户端登录
    client.send({"protocol":"cli_login", "role_id":argv[1]})
    game_mode.client = client

    print('等待服务器响应...')
    while not g.player:
        pass
    print('连接服务器成功')

    # 准备开始游戏
    game_mode.game_mode(screen)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
