import pygame
from abc import ABC, abstractmethod


class AbstractUIComponent(ABC):
    @abstractmethod
    def draw(self):
        pass


class TextInputBox(AbstractUIComponent):
    def __init__(self, screen, x, y, width, height, font_size=40):
        self.rect = pygame.Rect(x, y, width, height)
        self.screen = screen
        self.color = (255, 255, 255)
        self.text = ""
        self.font = pygame.font.Font(None, font_size)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect, 2)
        text_surface = self.font.render(self.text, True, self.color)
        self.screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))


class Slider(AbstractUIComponent):
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


# 方形按钮类，可以实现导入背景图片
class Button(AbstractUIComponent):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        font_size=20,
        text_color=(0, 0, 0),
        background_color=(255, 255, 255),
        background_image=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font("../fonts/FiraCode-Medium.ttf", font_size)
        self.text_color = text_color
        self.background_color = background_color
        self.text = text
        self.background_image = background_image

    # do something when clicked
    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True

    def draw(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, self.background_color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        # Lightening the button if the mouse is over it
        mouse_pos = pygame.mouse.get_pos()
        x, y, width, height = (
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height,
        )
        if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
            button_color = tuple(
                min(c + 30, 255) for c in self.background_color
            )  # Lighten the color
            pygame.draw.rect(screen, button_color, self.rect)
            screen.blit(text_surface, text_rect)


# 继承的圆形按钮
class CircleButton(Button):
    def __init__(
        self,
        x,
        y,
        radius,
        text,
        font_size=20,
        text_color=(0, 0, 0),
        background_color=(255, 255, 255),
    ):
        self.radius = radius
        width = radius * 2
        height = radius * 2
        super().__init__(
            x, y, width, height, text, font_size, text_color, background_color
        )

    def draw(self, screen):
        pygame.draw.circle(screen, self.background_color, self.rect.center, self.radius)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        # Lightening the button if the mouse is over it
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            button_color = tuple(
                min(c + 30, 255) for c in self.background_color
            )  # Lighten the color
            pygame.draw.circle(screen, button_color, self.rect.center, self.radius)
            screen.blit(text_surface, text_rect)


# 继承的圆角矩形按钮
class RoundedRectangleButton(Button):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        radius,
        text,
        font_size=20,
        text_color=(0, 0, 0),
        background_color=(255, 255, 255),
    ):
        self.radius = radius
        super().__init__(
            x, y, width, height, text, font_size, text_color, background_color
        )

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.background_color, self.rect, border_radius=self.radius
        )
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        # Lightening the button if the mouse is over it
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            button_color = tuple(
                min(c + 30, 255) for c in self.background_color
            )  # Lighten the color
            pygame.draw.rect(screen, button_color, self.rect, border_radius=self.radius)
            screen.blit(text_surface, text_rect)


# 复选框类
class Checkbox(AbstractUIComponent):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        font_size=20,
        text_color=(0, 0, 0),
        background_color=(255, 255, 255),
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color
        self.checked = False

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.background_color, (self.x, self.y, self.width, self.height)
        )
        pygame.draw.rect(
            screen,
            self.text_color,
            (self.x + 2, self.y + 2, self.width - 4, self.height - 4),
            2,
        )
        if self.checked:
            pygame.draw.line(
                screen,
                self.text_color,
                (self.x + 4, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height - 4),
                2,
            )
            pygame.draw.line(
                screen,
                self.text_color,
                (self.x + self.width // 2, self.y + self.height - 4),
                (self.x + self.width - 4, self.y + 4),
                2,
            )
        text_surface = pygame.font.Font(None, self.font_size).render(
            self.text, True, self.text_color
        )
        text_rect = text_surface.get_rect()
        text_rect.topleft = (self.x + self.width + 10, self.y)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (
                self.x <= event.pos[0] <= self.x + self.width
                and self.y <= event.pos[1] <= self.y + self.height
            ):
                self.checked = not self.checked


# 下拉菜单
class DropdownMenu(AbstractUIComponent):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        options,
        font_size=20,
        text_color=(0, 0, 0),
        background_color=(255, 255, 255),
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color
        self.is_open = False
        self.selected_option = None

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.background_color, (self.x, self.y, self.width, self.height)
        )
        pygame.draw.rect(
            screen,
            self.text_color,
            (self.x + 2, self.y + 2, self.width - 4, self.height - 4),
            2,
        )
        text_surface = pygame.font.Font(None, self.font_size).render(
            self.selected_option or "Select an option", True, self.text_color
        )
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
        screen.blit(text_surface, text_rect)

        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.x,
                    self.y + self.height + (i * self.height),
                    self.width,
                    self.height,
                )
                pygame.draw.rect(screen, self.background_color, option_rect)
                pygame.draw.rect(screen, self.text_color, option_rect, 2)
                option_surface = pygame.font.Font(None, self.font_size).render(
                    option, True, self.text_color
                )
                option_rect = option_surface.get_rect()
                option_rect.center = option_rect.center = (
                    self.x + self.width // 2,
                    self.y + self.height + (i * self.height) + self.height // 2,
                )
                screen.blit(option_surface, option_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (
                self.x <= event.pos[0] <= self.x + self.width
                and self.y <= event.pos[1] <= self.y + self.height
            ):
                self.is_open = not self.is_open
            elif self.is_open:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(
                        self.x,
                        self.y + self.height + (i * self.height),
                        self.width,
                        self.height,
                    )
                    if option_rect.collidepoint(event.pos):
                        self.selected_option = option
                        self.is_open = False
                        break

    def get_now_option(self):
        return self.selected_option


class Popup(AbstractUIComponent):
    def __init__(
        self,
        screen,
        message,
        button1_text="Button 1",
        button2_text="Button 2",
        x=None,
        y=None,
        width=300,
        height=200,
    ):
        if x is None:
            self.x = screen.get_width() // 2 - width // 2
        else:
            self.x = x
        if y is None:
            self.y = screen.get_height() // 2 - height // 2
        else:
            self.y = y
        self.width = width
        self.height = height
        self.screen = screen
        self.message = message
        self.button1_text = button1_text
        self.button2_text = button2_text
        self.running = False

        self.popup_rect = pygame.Rect(
            self.x, self.y, self.width, self.height
        )  # 设置弹窗的位置和大小
        self.close_button = Button(
            self.popup_rect.x + self.popup_rect.width - 30,
            self.popup_rect.y + 10,
            20,
            20,
            "X",
            font_size=15,
            text_color=(255, 255, 255),
            background_color=(255, 0, 0),
        )

        # 添加两个选择按钮
        self.button1 = Button(
            self.popup_rect.x + 50,
            self.popup_rect.y + self.popup_rect.height - 60,
            80,
            40,
            self.button1_text,
            font_size=15,
            text_color=(0, 0, 0),
            background_color=(200, 200, 200),
        )
        self.button2 = Button(
            self.popup_rect.x + 180,
            self.popup_rect.y + self.popup_rect.height - 60,
            80,
            40,
            self.button2_text,
            font_size=15,
            text_color=(0, 0, 0),
            background_color=(200, 200, 200),
        )

    def draw(self):
        # 绘制弹窗背景
        pygame.draw.rect(self.screen, (200, 200, 200), self.popup_rect)

        # 绘制弹窗内容
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.message, True, (0, 0, 0))
        text_rect = text_surface.get_rect(
            center=(
                self.popup_rect.x + self.popup_rect.width // 2,
                self.popup_rect.y + 40,
            )
        )
        self.screen.blit(text_surface, text_rect)

        # 绘制关闭按钮
        self.close_button.draw(self.screen)

        # 绘制选择按钮
        self.button1.draw(self.screen)
        self.button2.draw(self.screen)
