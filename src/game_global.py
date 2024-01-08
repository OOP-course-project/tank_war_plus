class Global:
    """
    游戏的全局共享变量
    """
    __instance = None

    client = None  # 客户端对象
    player = None  # 玩家本身
    game_start = False # 游戏是否开始
    round_start = False # 游戏回合是否已开始

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance


g = Global()
