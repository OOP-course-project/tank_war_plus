import pygame
import sys
import traceback
import wall
import tank
import food
import single_game
import double_game


def main():
    pygame.init()
    pygame.mixer.init()
    resolution = 630, 630
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Tank War")

    game_mode_selection = "double"

    print("game_mode_selection:", game_mode_selection)
    if game_mode_selection == "double":
        double_game.double_players(screen)

    if game_mode_selection == "single":
        single_game.single_player(screen)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
