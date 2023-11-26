import gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import numpy as np
import pygame
import tank_world
import torch


class Tank_game_env(gym.Env):
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((630, 630))
        self.double_players = False
        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=(630, 630, 3), dtype=np.uint8
        )
        self.action_space = gym.spaces.Discrete(
            5
        )  # Assume there are 5 possible actions

    def reset(self):
        # 重置游戏
        pygame.display.set_caption("Tank World")
        self.game = tank_world.TankWorld(self.screen)
        return self.get_observation()

    def step(self, action):
        # 在游戏中采取行动并返回下一个状态、奖励以及游戏是否结束的信息
        # 注意：根据你的游戏控制，修改行动处理
        self.game.update(action)
        self.game.draw()
        pygame.display.flip()
        self.clock.tick(60)
        return (
            self.get_observation(),
            self.game.get_reward(),
            self.game.is_game_over(),
            {},
        )

    def get_observation(self):
        # 将当前游戏屏幕捕获为观察值
        return pygame.surfarray.array3d(self.screen)


env = DummyVecEnv([lambda: Tank_game_env()])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = PPO("CnnPolicy", env, verbose=1, device=device)
model.learn(total_timesteps=10000)

model.save("tank_model")
