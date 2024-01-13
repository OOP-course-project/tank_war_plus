# Tank World Plus

Tank World Plus is a large assignment we completed in our Advanced Programming course in SCUT. This is a tank battle game based on Pygame, with rich game elements and interactivity. Below is some information about this project and instructions for use.

## Project structure

tank_war_plus
├── README.md
├── fonts
│   └── FiraCode-Medium.ttf
├── image
│   ├── TankWar.png
│   ├── bullet_up.png
│   └── ...
├── maps
│   ├── initial_points.json
│   ├── random_map.json
│   └── self_made_map.json
├── music
│   ├── Gunfire.wav
│   └── ...
└── src
    ├── agent.py
    ├── bullet.py
    ├── bullet_printer.py
    ├── client.py
    ├── food.py
    ├── main.py
    ├── net_tank_world.py
    ├── utilise.py
    └── ...

## Game starts

```shell
git clone https://github.com/OOP-course-project/tank_war_plus.git
conda create -n tank_war python=3.9
conda activate tank_war
cd tank_war_plus
pip install -r requirements.txt
cd src
python main.py
```

## Mode selection

Tank World offers a variety of game modes to meet the needs of different players:

1. **Single player mode**:
    - Players can challenge the game alone, defeat enemy tanks and defend the base.

2. **Local two-player mode**:
    - Two players share the same device and operate their respective tanks through the keyboard, working together or against each other.

3. **LAN online two-player mode**:
    - Two players work together to protect the base and then compete for kill scores.
    - When you enter online mode, we default to player one starting the server, but player one and player two need to fill in the IP address of player one's computer and the port they want to use in the settings before starting online mode to succeed. online
    
4. **Level-breaking mode**:
    - Players need to challenge levels with gradually increasing difficulty. Except for the first level, the maps of each level are randomly generated, full of exciting randomness.

## How to play the game

### Control Method

Player 1: W (top), S (bottom), A (left), D (right), Space (shoot bullets)
Player 2: ↑ (up), ↓ (down), ← (left), → (right), 0 on the keypad(shoot bullets)

### Game Goals:

1. Destroy enemy tanks and defend the base.
2. You can get a point if you kill an enemy tank.
3. If your base is attacked by an enemy tank, or your health reaches zero (that is, it was attacked three times), you will lose the game.

## Special feature

1. In the setting, we can freely edit and save the map. We can use the map we edited for local games.
2. In the setting, we can freely edit the map and save the map. We can use the map we edited for local games.
3. We use the BFS algorithm to make behavioral decisions on enemy tanks to track attacking player tanks.
4. We also try use reinforce learning algorithm to play our game, If you want to try it, you should do these

```shell
cd ..
pip install -r requirements_rfl.txt
cd src
python agent.py 
```



