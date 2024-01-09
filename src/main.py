import pygame
import sys
import traceback
import wall
import tank
import food
from tank_world import Tank_world
from utilise import *


def main():
    screen = init_pygame((630, 630))
    pygame.display.set_caption("Tank War Plus")
    background = init_ui_background()

    while True:
        screen.blit(background, (0, 0))
        button_width = 200
        button_height = 100

        draw_button(
            screen,
            "rounded_rectangle",
            (220, 20, 20),
            350,
            120,
            button_width,
            button_height,
            "Single Game",
            radius=10,
        )

        draw_button(
            screen,
            "rounded_rectangle",
            (30, 220, 30),
            350,
            300,
            button_width,
            button_height,
            "Double Game",
            radius=10,
        )

        draw_button(
            screen,
            "rectangle",
            (210, 180, 140),
            0,
            400,
            button_width,
            button_height,
            "Settings",
        )

        pygame.display.flip()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                if (
                    350 <= mouse_pos[0] <= 350 + button_width
                    and 120 <= mouse_pos[1] <= 120 + button_height
                ):
                    button_color = tuple(
                        min(c + 30, 255) for c in (255, 0, 0)
                    )  # Lighten the color
                elif (
                    350 <= mouse_pos[0] <= 350 + button_width
                    and 300 <= mouse_pos[1] <= 300 + button_height
                ):
                    button_color = tuple(
                        min(c + 30, 255) for c in (0, 255, 0)
                    )  # Lighten the color
                elif (
                    0 <= mouse_pos[0] <= button_width
                    and 400 <= mouse_pos[1] <= 400 + button_height
                ):
                    button_color = tuple(
                        min(c + 30, 255) for c in (210, 180, 140)
                    )  # Lighten the color
                else:
                    button_color = (255, 0, 0)

                draw_button(
                    screen,
                    "rounded_rectangle",
                    button_color,
                    350,
                    120,
                    button_width,
                    button_height,
                    "Single Game",
                    radius=10,
                )
                draw_button(
                    screen,
                    "rounded_rectangle",
                    button_color,
                    350,
                    300,
                    button_width,
                    button_height,
                    "Double Game",
                    radius=10,
                )
                draw_button(
                    screen,
                    "rectangle",
                    button_color,
                    0,
                    400,
                    button_width,
                    button_height,
                    "Settings",
                )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    350 <= mouse_pos[0] <= 350 + button_width
                    and 120 <= mouse_pos[1] <= 120 + button_height
                ):
                    tw = Tank_world(screen, double_players=False)
                    tw.run()
                elif (
                    350 <= mouse_pos[0] <= 350 + button_width
                    and 300 <= mouse_pos[1] <= 300 + button_height
                ):
                    tw = Tank_world(screen, double_players=True)
                    tw.run()
                elif (
                    0 <= mouse_pos[0] <= button_width
                    and 400 <= mouse_pos[1] <= 400 + button_height
                ):
                    # Add settings functionality here
                    pass


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
