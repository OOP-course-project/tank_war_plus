import pygame
import sys
import traceback
import wall
import tank
import food
import game_mode


def main():
    pygame.init()
    pygame.mixer.init()
    resolution = 630, 630
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Tank War")

    game_mode_selection = "double"

    print("game_mode_selection:", game_mode_selection)
    if game_mode_selection == "double":
        game_mode.game_mode(screen, double_players=True)

    if game_mode_selection == "single":
        game_mode.game_mode(screen)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
