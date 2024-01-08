import json
import traceback
from threading import Thread

import tank
import pygame
from game_mode import globalV, player_tanks_list
from game_global import g

class Player:
    """
    玩家类
    """
    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']  # 玩家昵称
        self.uuid = kwargs['uuid']  # 玩家的唯一标识
        self.role_id = kwargs['role_id']  # 玩家角色id
        self.score = 0

class Client:
    """
    客户端与服务端网络交互相关的操作
    """
    def __init__(self, socket, game_scene):
        self.socket = socket  # 客户端socket
        # self.game = game_scene  # GameScene对象
        # 创建一个线程专门处理数据接收
        thread = Thread(target=self.recv_data)
        thread.setDaemon(True)
        thread.start()

    def data_handler(self):
        # 给每个连接创建一个独立的线程进行管理
        thread = Thread(target=self.recv_data)
        thread.setDaemon(True)
        thread.start()

    def deal_data(self, bytes):
        """
        处理数据
        """
        # 将字节流转成字符串
        pck = bytes.decode()
        # 切割数据包
        pck = pck.split('|#|')
        # 处理每一个协议,最后一个是空字符串，不用处理它
        for str_protocol in pck[:-1]:
            try:
                protocol = json.loads(str_protocol)
            except json.decoder.JSONDecodeError:
                continue
            # 根据协议中的protocol字段，直接调用相应的函数处理
            self.protocol_handler(protocol)

    def recv_data(self):
        # 接收数据
        try:
            while True:
                bytes = self.socket.recv(4096)
                if len(bytes) == 0:
                    self.socket.close()
                    # TODO:掉线处理
                    break
                # 处理数据
                self.deal_data(bytes)
                
        except:
            self.socket.close()
            # TODO:异常掉线处理
            traceback.print_exc()

    def send(self, py_obj):
        """
        给服务器发送协议包
        py_obj:python的字典或者list
        """
        self.socket.sendall((json.dumps(py_obj, ensure_ascii=False) + '|#|').encode())

    def protocol_handler(self, protocol):
        """
        处理服务端发来的协议
        """
        if protocol['protocol'] == 'ser_login':
            # 登录协议的相关逻辑
            if not protocol['result']:
                # 登录失败，继续调用登录方法
                print("登录失败：", protocol['msg'])
                return
            # 登录成功，并创建玩家
            g.player = Player(role_id=protocol['player_data']['role_id'],name=protocol['player_data']['nickname'], uuid=protocol['player_data']['uuid'])
        elif protocol['protocol'] == 'ser_player_list':
            print(protocol)
        elif protocol['protocol'] == 'game_start':
            g.round_start = True
            if not g.game_start:
                g.game_start = True
            
        elif protocol['protocol'] == 'game_over':
            g.round_start = False
        elif protocol['protocol'] == 'ser_move':


            role_id = protocol['player_data']['role_id']
            all_tank_group = globalV['all_tank_group']
            back_ground = globalV['back_ground']
            
            frame = protocol['player_data']['t']
            if frame > player_tanks_list[role_id - 1].frame:
                player_tanks_list[role_id - 1].frame = frame
                player_tanks_list[role_id - 1].moving1 = 7
                player_tanks_list[role_id - 1].direction = protocol['player_data']['dir']
                all_tank_group.remove(player_tanks_list[role_id - 1])
                if player_tanks_list[role_id - 1].move_func(
                    all_tank_group, back_ground.brick_group, back_ground.iron_group
                ):
                    player_tanks_list[role_id - 1].moving1 = 0
                all_tank_group.add(player_tanks_list[role_id - 1])
        elif protocol['protocol'] == 'player_pos':
            role_id = protocol['player_data']['role_id']
            player_tanks_list[role_id - 1].direction = protocol['player_data']['dir']
            player_tanks_list[role_id - 1].rect.left = protocol['player_data']['left']
            player_tanks_list[role_id - 1].rect.top = protocol['player_data']['top']
            

        elif protocol['protocol'] == 'player_shoot':
            role_id = protocol['player_data']['role_id']
            player_tanks_list[role_id - 1].shoot()
            player_tanks_list[role_id - 1].bullet_not_cooling = True
        elif protocol['protocol'] == 'player_injured':
            role_id = protocol['role_id']
            player_tanks_list[role_id - 1].life -= 1
        elif protocol['protocol'] == 'player_die':
            role_id = protocol['role_id']
            player_tanks_list[role_id - 1].life = 0
        elif protocol['protocol'] == 'enemy_birth':
            all_tank_group = globalV['all_tank_group']
            enemy_tank_group = globalV['enemy_tank_group']
            tank.Enemy_tank.tank_id = protocol['player_data']['tank_id']
            enemy = tank.Enemy_tank()
            all_tank_group.add(enemy)
            enemy_tank_group.add(enemy)

        elif protocol['protocol'] == 'enemy_move':
            if 'enemy_tank_group' in globalV:
                enemy_tank_group = globalV['enemy_tank_group']
                info = protocol['player_data']['info']
                for enemy_tank in enemy_tank_group:
                    tank_id = str(enemy_tank.tank_id)
                    if tank_id in info:
                        enemy_tank.move_sync(info[tank_id][0],info[tank_id][1],info[tank_id][2])
                    else: 
                        if len(enemy_tank_group) > 3:
                            enemy_tank.life = 0
                    
        elif protocol['protocol'] == 'enemy_shoot':
            if 'enemy_tank_group' in globalV:
                enemy_tank_group = globalV['enemy_tank_group']
                enemy_bullet_group = globalV['enemy_bullet_group']
                for enemy_tank in enemy_tank_group:
                    enemy_bullet_group.remove(enemy_tank.bullet)
                    enemy_tank.shoot()
                    enemy_bullet_group.add(enemy_tank.bullet)
                    enemy_tank.bullet_not_cooling = False


    def login(self, username, password):
        """
        登录
        """
        data = {
            'protocol': 'cli_login',
            'username': username,
            'password': password
        }
        self.send(data)

    def move(self, player):
        """
        玩家移动
        """
        data = {
            'protocol': 'cli_move',
            'x': player.next_mx,
            'y': player.next_my
        }
        self.send(data)

