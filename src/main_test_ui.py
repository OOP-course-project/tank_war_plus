import pygame
import sys
import traceback
import random
import game_mode

# Constants for colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def draw_button(screen, button_type, color, x, y, width, height, text, radius=None):
    button_color = color

    # Check if mouse is hovering over the button
    mouse_pos = pygame.mouse.get_pos()
    if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
        button_color = tuple(min(c + 30, 255) for c in color)  # Lighten the color

    if button_type == "rounded_rectangle":
        if radius is None:
            radius = 10  # default radius

        pygame.draw.rect(
            screen, button_color, (x, y, width, height), border_radius=radius
        )
    elif button_type == "rectangle":
        pygame.draw.rect(screen, button_color, (x, y, width, height))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 1)

    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
    screen.blit(text_surface, text_rect)


def main():
    pygame.init()
    resolution = 630, 630
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Tank War")

    single_game_girl = pygame.image.load("../image/single_game_girl.png")
    double_game_girls = pygame.image.load("../image/double_game_girls.png")

    backgrounds = [single_game_girl, double_game_girls]
    background = random.choice(backgrounds)

    running = True
    while running:
        screen.fill(BLACK)
        screen.blit(background, (0, 0))

        button_width = 200
        button_height = 100

        # Draw Single Game button (rounded rectangle, red)
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

        # Draw Double Game button (rounded rectangle, green)
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

        # Draw Settings button (rectangle, tan)
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
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
                mouse_pos = pygame.mouse.get_pos()
                if (
                    350 <= mouse_pos[0] <= 350 + button_width
                    and 120 <= mouse_pos[1] <= 120 + button_height
                ):
                    game_mode.game_mode(screen)
                elif (
                    350 <= mouse_pos[0] <= 350 + button_width
                    and 300 <= mouse_pos[1] <= 300 + button_height
                ):
                    game_mode.game_mode(screen, double_players=True)
                elif (
                    0 <= mouse_pos[0] <= button_width
                    and 400 <= mouse_pos[1] <= 400 + button_height
                ):
                    # Add settings functionality here
                    pass

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
