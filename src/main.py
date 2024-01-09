import pygame
import sys
import traceback
import wall
import tank
import food
from tank_world import Tank_world


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((630, 630))
    tw1 = Tank_world(screen, double_players=False)
    tw2 = Tank_world(screen, double_players=True)

    game_mode_selection = "single"

    print("game_mode_selection:", game_mode_selection)
    if game_mode_selection == "double":
        tw2.run()

    if game_mode_selection == "single":
        tw1.run()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
