# -*- coding: utf-8 -*-
import datetime
import json
import socket
import time
import traceback
import uuid
import random
from threading import Thread
import signal

def exit_(s, f):
    print('---')
    exit(0)

signal.signal(signal.SIGINT, exit_)
signal.signal(signal.SIGTERM, exit_)

random.seed(1)

class Server:
    """
    服务端主类
    """
    __user_cls = None

    @staticmethod
    def write_log(msg):
        cur_time = datetime.datetime.now()
        s = "[" + str(cur_time) + "]" + msg
        print(s)

    @staticmethod
    def write_in_log_file(msg):
        """
        把一些重要的信息写入日志文件
        """
        with open('./' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log', mode='a+',
                  encoding='utf8') as file:
            cur_time = datetime.datetime.now()
            s = "[" + str(cur_time) + "]" + msg
            file.write(s)

    def __init__(self, ip, port):
        self.connections = []  # 所有客户端连接
        self.write_log('服务器启动中，请稍候...')
        try:
            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 监听者，用于接收新的socket连接
            self.listener.bind((ip, port))  # 绑定ip、端口
            self.listener.settimeout(1.5)
            self.listener.listen(5)  # 最大等待数
        except:
            self.write_log('服务器启动失败，请检查ip端口是否被占用。详细原因请查看日志文件')
            self.write_in_log_file(traceback.format_exc())

        if self.__user_cls is None:
            self.write_log('服务器启动失败，未注册用户自定义类')
            return

        self.write_log('服务器启动成功：{}:{}'.format(ip, port))

        try:
            while True:
                try:
                    client, _ = self.listener.accept()  # 阻塞，等待客户端连接
                    user = self.__user_cls(client, self.connections)
                    self.connections.append(user)
                    self.write_log('有新连接进入，当前连接数：{}'.format(len(self.connections)))
                except socket.timeout:
                    pass
                except KeyboardInterrupt:
                    pass
        except KeyboardInterrupt:
            self.listener.close()

    @classmethod
    def register_cls(cls, sub_cls):
        """
        注册玩家的自定义类
        """
        if not issubclass(sub_cls, Connection):
            cls.write_log('注册用户自定义类失败，类型不匹配')
            return

        cls.__user_cls = sub_cls


class Connection:
    """
    连接类，每个玩家的socket连接都是一个Connection对象
    """

    def __init__(self, socket, connections):
        self.socket = socket
        self.connections = connections
        self.data_handler()

    def data_handler(self):
        # 为每个连接创建一个独立的线程进行管理
        thread = Thread(target=self.recv_data)
        thread.setDaemon(True)
        thread.start()

    def recv_data(self):
        # 接收客户端传递到服务端的数据
        bytes = None
        try:
            while True:
                bytes = self.socket.recv(4096)  # 我们这里只做一个简单的服务端框架，只做粘包不做分包处理。
                if len(bytes) == 0:
                    Server.write_log('玩家离线：' + str(self.game_data))
                    self.socket.close()
                    # 删除连接
                    self.connections.remove(self)
                    break
                # 处理数据
                self.deal_data(bytes)
                print(bytes)
        except:
            self.socket.close()
            self.connections.remove(self)
            Server.write_log('用户异常数据：' + bytes.decode() + '\n' + '，该玩家已被强制下线')
            Server.write_in_log_file(traceback.format_exc())

    def deal_data(self, bytes):
        """
        由子类来实现数据处理过程
        """
        raise NotImplementedError


@Server.register_cls
class Player(Connection):

    def __init__(self, *args):
        self.login_state = False  # 玩家登录状态
        self.game_data = None  # 玩家在游戏中的相关数据
        self.protocol_handler = ProtocolHandler()  # 协议处理对象
        super().__init__(*args)

    def deal_data(self, bytes):
        # 将字节流转成字符串
        pck = bytes.decode()
        # 切割数据包
        pck = pck.split('|#|')
        # 处理每一个协议,最后一个是空字符串，不用处理它
        for str_protocol in pck[:-1]:
            protocol = json.loads(str_protocol)
            # 根据协议中的protocol字段，调用相应的函数处理
            self.protocol_handler(self, protocol)

    def send(self, data):
        """
        给玩家发送协议包
        data:python的字典或者list
        """
        self.socket.sendall((json.dumps(data, ensure_ascii=False) + '|#|').encode())

    def send_all_player(self, data):
        """
        把这个数据包发送给所有在线的玩家（包括自己）
        """
        
        for player in self.connections:
            if player.login_state:
                player.send(data)

    def send_without_self(self, data):
        """
        发送给除了自己的所有在线玩家
        """
        for player in self.connections:
            if player is not self and player.login_state:
                player.send(data)


class ProtocolHandler:
    """
    处理客户端传递过来的数据协议
    """

    def __call__(self, player, protocol):
        protocol_name = protocol['protocol']
        if not hasattr(self, protocol_name):
            return None
        # 调用与协议同名的函数去处理
        method = getattr(self, protocol_name)
        result = method(player, protocol)
        return result

    @staticmethod
    def cli_login(player, protocol):
        """
        客户端玩家登录
        """

        role_id = protocol.get('role_id')  # 玩家角色id

        # 登录成功
        player.login_state = True
        player.game_data = {
            'uuid': uuid.uuid4().hex,
            'nickname': 'Player_' + str(role_id),
            'role_id': int(role_id)
        }

        # 发送登录成功协议
        player.send({"protocol": "ser_login", "result": True, "player_data": player.game_data})

        # 发送上线信息给其他玩家
        player.send_without_self({"protocol": "ser_online", "player_data": player.game_data})

        player_list = []
        for p in player.connections:
            if p is not player and p.login_state:
                player_list.append(p.game_data)
        # 发送当前在线玩家列表给自己（不包括自己）
        player.send({"protocol": "ser_player_list", "player_list": player_list})

        if len(player_list) > 0:
            player.send_all_player({"protocol": "game_start"})

    @staticmethod
    def cli_move(player, protocol):
        """
        客户端玩家坦克移动
        """
        # 如果玩家未登录，则不做处理
        if not player.login_state:
            return

        # 客户端玩家坦克移动的位置
        player.game_data['dir'] = protocol.get('dir')
        player.game_data['x'] = protocol.get('x')
        player.game_data['y'] = protocol.get('y')

        # 告诉所有玩家当前玩家坦克的位置发生变化
        player.send_all_player({"protocol": "ser_move", "player_data": player.game_data})

    @staticmethod
    def game_start(player, protocol):
        """
        游戏开始
        """
        # 服务器通知各个客户端游戏开始
        if not player.login_state:
            return

        player.send_all_player({"protocol": "game_start", "player_data": player.game_data})

    @staticmethod
    def game_over(player, protocol):
        """
        游戏结束
        """
        # 服务器通知各个客户端游戏结束
        if not player.login_state:
            return

        player.send_all_player({"protocol": "game_over", "player_data": player.game_data})
    @staticmethod
    def player_shoot(player, protocol):
        """
        通知所有客户端玩家坦克发生射击动作
        """
        # 如果玩家未登录，则不做处理
        if not player.login_state:
            return

        # 告诉其他玩家当前玩家坦克发射出子弹
        # player.send_without_self({"protocol": "ser_move", "player_data": player.game_data})
        player.send_all_player({"protocol": "player_shoot", "player_data": player.game_data})

    @staticmethod
    def enemy_shoot(player, protocol):
        """
        通知所有客户端敌人坦克发生射击动作
        """
        # 如果玩家未登录，则不做处理
        if not player.login_state:
            return

        # 告诉所有玩家敌人坦克发射出子弹
        player.send_all_player({"protocol": "enemy_shoot", "player_data": player.game_data})

    @staticmethod
    def enemy_birth(player, protocol):
        """
        通知所有客户端有新敌人出现
        """
        # 如果玩家未登录，则不做处理
        if not player.login_state:
            return
    
        player.game_data['kind'] = random.choice([1, 2, 3, 4])

        # 告诉所有玩家有新的敌人出现
        player.send_all_player({"protocol": "enemy_birth", "player_data": player.game_data})

    @staticmethod
    def enemy_move(player, protocol):
        """
        通知所有客户端敌人坦克正在移动
        """
        # 如果玩家未登录，则不做处理
        if not player.login_state:
            return

        # 敌人的移动信息
        player.game_data['info'] = protocol.get('info')

        # 告诉所有玩家敌人的坦克发生了移动
        player.send_all_player({"protocol": "enemy_move", "player_data": player.game_data})



if __name__ == '__main__':
    # 绑定0.0.0.0地址，这样局域网内的电脑才能连接到此电脑
    server = Server('0.0.0.0', 8888)