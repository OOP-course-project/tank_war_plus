import pygame
import random


class Slider:
    def __init__(
        self, screen, length, initial_position, color_line, color_button, button_radius
    ):
        self.screen = screen
        self.length = length
        self.position = initial_position
        self.color_line = color_line
        self.color_button = color_button
        self.button_radius = button_radius

    def draw(self):
        # 绘制滑块轨道
        pygame.draw.line(
            self.screen,
            self.color_line,
            (50, self.position[1]),
            (550, self.position[1]),
            5,
        )
        # 绘制滑块按钮
        pygame.draw.circle(
            self.screen, self.color_button, self.position, self.button_radius
        )

    def update_position(self, new_position):
        # 更新滑块按钮位置
        self.position = new_position


def change_image(image, direction):
    if direction == "up":
        return image
    elif direction == "down":
        return pygame.transform.rotate(image, 180)
    elif direction == "left":
        return pygame.transform.rotate(image, 90)
    elif direction == "right":
        return pygame.transform.rotate(image, 270)


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


def init_pygame(resolution):
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode(resolution)
    return screen


def init_ui_background():
    single_game_girl = pygame.image.load("../image/single_game_girl.png")
    double_game_girls = pygame.image.load("../image/double_game_girls.png")
    backgrounds = [single_game_girl, double_game_girls]
    background = random.choice(backgrounds)
    return background
