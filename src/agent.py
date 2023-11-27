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
        self.game = tank_world.Tank_world(
            self.screen, double_players=self.double_players
        )
        self.observation_space = gym.spaces.Dict(
            {
                "brick_pos": gym.spaces.Box(
                    low=0, high=1, shape=(26, 26), dtype=np.uint8
                ),
                "iron_pos": gym.spaces.Box(
                    low=0, high=1, shape=(26, 26), dtype=np.uint8
                ),
                "enemy_pos": gym.spaces.Box(
                    low=0, high=1, shape=(13, 13), dtype=np.uint8
                ),
                "player_pos": gym.spaces.Box(
                    low=0, high=1, shape=(13, 13), dtype=np.uint8
                ),
                "bullet_pos": gym.spaces.Box(
                    low=0, high=1, shape=(52, 52), dtype=np.uint8
                ),
            }
        )
        self.action_space = gym.spaces.Discrete(6)

    def reset(self):
        # 重置游戏
        pygame.display.set_caption("Tank World")
        self.game = tank_world.Tank_world(self.screen)
        return self.get_observation()

    def step(self, action):
        # 在游戏中采取行动并返回下一个状态、奖励以及游戏是否结束的信息
        # 注意：根据你的游戏控制，修改行动处理
        if not self.game.moving1:
            if action == 0:
                self.game.tank_moving(self.game.player_tank1, "up")
            elif action == 1:
                self.game.tank_moving(self.game.player_tank1, "down")
            elif action == 2:
                self.game.tank_moving(self.game.player_tank1, "left")
            elif action == 3:
                self.game.tank_moving(self.game.player_tank1, "right")
        if action == 4:
            self.game.tank_shoot(self.game.player_tank1)
        if action == 5:
            pass
        self.game.update()
        self.game.draw(self.game.current_time)
        pygame.display.flip()
        self.game.clock.tick(60)
        
        observation = self.get_observation()
        reward = self.game.get_reward()
        done = self.game.is_game_over()

        if done:
            reward = reward - 5
        
        return observation, reward, done, {}

    def get_observation(self):
        # 将当前游戏屏幕捕获为观察值
        brick_pos = np.array(self.game.brick_pos)
        iron_pos = np.array(self.game.iron_pos)
        enemy_pos = np.array(self.game.enemy_pos)
        player_pos = np.array(self.game.player_pos)
        bullet_pos = np.array(self.game.bullet_pos)
        observation = {
            "brick_pos": brick_pos,
            "iron_pos": iron_pos,
            "enemy_pos": enemy_pos,
            "player_pos": player_pos,
            "bullet_pos": bullet_pos,
        }
        return observation


env = DummyVecEnv([lambda: Tank_game_env()])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = PPO("MultiInputPolicy", env, verbose=1, device=device)
model.learn(total_timesteps=50000)

model.save("tank_model")
