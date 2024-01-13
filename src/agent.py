import gymnasium
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import numpy as np
import pygame
import tank_world
import torch


class Tank_game_env(gymnasium.Env):
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((630, 630))
        self.double_players = False
        self.game = None
        self.observation_space = gymnasium.spaces.Dict(
            {
                "brick_pos": gymnasium.spaces.Box(
                    low=0, high=1, shape=(26, 26), dtype=np.uint8
                ),
                "iron_pos": gymnasium.spaces.Box(
                    low=0, high=1, shape=(26, 26), dtype=np.uint8
                ),
                "enemy_pos": gymnasium.spaces.Box(
                    low=0, high=1, shape=(13, 13), dtype=np.uint8
                ),
                "player_pos": gymnasium.spaces.Box(
                    low=0, high=1, shape=(13, 13), dtype=np.uint8
                ),
                "bullet_pos": gymnasium.spaces.Box(
                    low=0, high=1, shape=(52, 52), dtype=np.uint8
                ),
            }
        )
        self.action_space = gymnasium.spaces.Discrete(6)

    def reset(self, seed=None):
        self.game = tank_world.Tank_world(
            self.screen, double_players=self.double_players, BFS_open=True
        )
        return self.get_observation(), {}

    def step(self, action):
        if action == 0:
            self.game.tank_moving(self.game.player_tank1, "up")
        elif action == 1:
            self.game.tank_moving(self.game.player_tank1, "down")
        elif action == 2:
            self.game.tank_moving(self.game.player_tank1, "left")
        elif action == 3:
            self.game.tank_moving(self.game.player_tank1, "right")
        elif action == 4:
            self.game.tank_shoot(self.game.player_tank1)
        elif action == 5:
            pass
        self.game.update()
        pygame.display.flip()
        self.game.clock.tick(60)

        observation = self.get_observation()
        reward = self.game.get_reward()
        done = self.game.is_game_over()

        if done:
            reward = reward - 1

        return observation, reward, done, False, {}

    def get_observation(self):
        # observation = pygame.surfarray.array3d(self.screen)
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


checkpoint_callback = CheckpointCallback(
    save_freq=20000,  # Save the model every 20000 steps
    save_path="./checkpoints_new/",
    name_prefix="tank_model",
)

env = DummyVecEnv([lambda: Tank_game_env()])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = PPO(
    "MultiInputPolicy",
    env,
    verbose=1,
    learning_rate=3e-4,
    device=device,
    batch_size=128,
    tensorboard_log="./PPOTankWorld_tensorboard/",
)

# model = PPO.load(
#     "./tank_model.zip",
#     env=env,
#     device=device,
#     tensorboard_log="./PPOTankWorld_tensorboard/",
# )

model.learn(total_timesteps=300000)

model.save("tank_model")
