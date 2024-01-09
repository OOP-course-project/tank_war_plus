import pygame
import sys
import traceback
import wall
import tank
import food
from tank_world import Tank_world
from utilise import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def main():
    screen = init_pygame((630, 630))
    background = init_ui_background()
    game_mode_selection = "single"
    print("game_mode_selection:", game_mode_selection)

    if game_mode_selection == "single":
        tw = Tank_world(screen, background, game_mode_selection)
    elif game_mode_selection == "double":
        tw = Tank_world(screen, background, game_mode_selection)

    tw.run()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
