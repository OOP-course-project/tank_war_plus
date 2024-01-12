# 导入所需的模块
import pygame
import pygame.freetype  # 引入 pygame.freetype 用于更高级的字体处理
import json
import sys

# 初始化 pygame 和 pygame.freetype
pygame.init()
pygame.freetype.init()

# 设置全局颜色和字体
white = (255, 255, 255)
black = (0, 0, 0)
grey = (128, 128, 128)
grid_color = (150, 150, 150)
selection_color = (0, 128, 0)
text_color = (255, 255, 255)
GAME_FONT = pygame.freetype.SysFont(None, 36)

# # 定义全局变量
# hover_start_time = None
# hover_position = None

# 定义 UI 风格设置
style = {
    # 按钮样式
    "button": {
        "normal_color": (100, 100, 100),
        "hover_color": (100, 160, 200),  # 鼠标悬停时的颜色
        "click_color": (50, 90, 140),  # 按钮点击状态颜色
        "text_color": (255, 255, 255),  # 文本颜色
        "border_radius": 8,  # 边框圆角半径
    },
    # 字体样式
    "font": pygame.freetype.SysFont(None, 24),
}

# 设置资源路径
resource_paths = {
    "cursor_image": "../image/cursor.png",
    "click_sound": "../music/click.wav",
    "brick_image": "../image/brick.png",
    "iron_image": "../image/iron.png",
    # 更多资源路径可以在这里添加
}


# 资源管理器类，用于加载和管理资源
class ResourceManager:
    def __init__(self, resource_paths):
        self.resource_paths = resource_paths
        pygame.mixer.init()

    def load_image(self, key):
        """根据键从字典中获取路径来加载图像资源"""
        file_path = self.resource_paths.get(key)
        try:
            image = pygame.image.load(file_path)
            return image
        except pygame.error as e:
            print(f"无法加载图片 {file_path}: {e}")
            return None

    def load_sound(self, key):
        """根据键从字典中获取路径来加载声音资源"""
        file_path = self.resource_paths.get(key)
        try:
            sound = pygame.mixer.Sound(file_path)
            return sound
        except pygame.error as e:
            print(f"无法加载音效 {file_path}: {e}")
            return None


# 加载资源
resource_manager = ResourceManager(resource_paths)
click_sound = resource_manager.load_sound("click_sound")
brick_image = resource_manager.load_image("brick_image")
iron_image = resource_manager.load_image("iron_image")
cursor_image = resource_manager.load_image("cursor_image")

# 调整光标图像尺寸
cursor_image = pygame.transform.scale(cursor_image, (16, 16))
cursor_rect = cursor_image.get_rect()
# pygame.mouse.set_visible(False)  # 隐藏默认光标


# 定义按钮类
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        # 动画相关属性
        self.original_rect = self.rect.copy()  # 保存原始大小
        self.clicked = False  # 按钮是否被点击
        self.click_animation_count = 0  # 点击动画计数器
        # 使用样式变量来初始化按钮颜色
        self.color = style["button"]["normal_color"]
        self.hover_color = style["button"]["hover_color"]
        self.click_color = style["button"]["click_color"]
        self.current_color = self.color

    def handle_click(self):
        if not self.clicked:  # 只有当当前没有动画正在播放时才开始新的动画
            self.clicked = True
            self.click_animation_count = 10  # 设置动画持续时间

    def update(self, mouse_pos):
        # 检测鼠标是否悬停在按钮上
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.clicked:
            if self.click_animation_count > 0:
                change = -2 if self.click_animation_count > 5 else 2
                self.rect.inflate_ip(change, change)
                self.current_color = self.click_color  # 在动画期间使用点击颜色
                self.click_animation_count -= 1
            else:
                self.rect = self.original_rect.copy()
                self.clicked = False
                self.current_color = (
                    self.hover_color if self.is_hovered else self.color
                )  # 动画结束后根据悬停状态更新颜色
        elif self.is_hovered:
            self.current_color = self.hover_color  # 悬停时更新颜色
            if self.rect.width < self.original_rect.width + 6:  # 放大限制
                self.rect.inflate_ip(2, 2)  # 每次放大2像素
        else:
            self.current_color = self.color  # 正常状态的颜色
            if self.rect.width > self.original_rect.width:
                self.rect.inflate_ip(-2, -2)  # 缩小回原始大小

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.current_color,
            self.rect,
            border_radius=style["button"]["border_radius"],
        )
        text_render, text_rect = style["font"].render(
            self.text, style["button"]["text_color"]
        )
        text_rect.center = self.rect.center  # 确保文本居中
        screen.blit(text_render, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)


# 创建按钮实例


class UI:
    def __init__(self, screen, font, undo_stack):
        self.screen = screen
        self.font = font
        self.ui_area = pygame.Rect(0, 0, 200, screen.get_height())
        self.icon_rects = {}  # 初始化用于存储图标矩形的字典
        self.message = None
        self.message_start_time = None
        self.message_duration = 2000  # 消息显示时间，单位为毫秒
        self.undo_stack = undo_stack

    def draw_ui(self, element_images, grey, white):
        """绘制 UI 背景和元素"""
        self.screen.fill(grey, self.ui_area)
        y_offset = 10
        for element, image in element_images.items():
            text = self.font.render(element.capitalize(), True, white)
            self.screen.blit(text, (10, y_offset))
            y_offset += text.get_height() + 5
            image_rect = self.screen.blit(image, (10, y_offset))
            self.icon_rects[element] = image_rect  # 更新图标的矩形区域
            y_offset += image.get_height() + 20

        # 绘制历史记录的背景框
        history_bg_rect = pygame.Rect(0, 500, 200, 100)  # 将历史记录放在底部
        pygame.draw.rect(self.screen, (50, 50, 50), history_bg_rect)  # 深灰色背景

        # 绘制历史记录标题
        y_offset = 510  # 从背景框下方开始
        text = font.render("History", True, white)
        self.screen.blit(text, (10, y_offset))
        y_offset += text.get_height() + 5

        # 绘制历史记录内容
        for action, element, position in reversed(self.undo_stack[-2:]):  # 显示最近的2个操作
            action_symbol = "+" if action == "add" else "-"
            element_abbr = element[0]  # 取元素名称的第一个字母作为缩写
            action_text = (
                f"{action_symbol}{element_abbr} @ {position['x']},{position['y']}"
            )
            text = font.render(action_text, True, white)
            self.screen.blit(text, (10, y_offset))
            y_offset += text.get_height() + 5

    def draw_help(self, help_text):
        """绘制帮助文本"""
        padding = 10
        text_width = max(self.font.size(line)[0] for line in help_text) + padding * 2
        text_height = sum(self.font.size(line)[1] for line in help_text) + padding * (
            len(help_text) + 1
        )
        bg_rect = pygame.Rect(
            self.screen.get_width() - text_width - 20, 20, text_width, text_height
        )

        # 绘制半透明背景框
        bg_color = (0, 0, 0, 128)
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(128)
        s.fill(bg_color)
        self.screen.blit(s, (bg_rect.x, bg_rect.y))

        # 绘制帮助文本
        y = bg_rect.y + padding
        for line in help_text:
            text_surface = self.font.render(line, True, white)
            self.screen.blit(text_surface, (bg_rect.x + padding, y))
            y += text_surface.get_height() + padding

    def show_message(self, message):
        # 显示一条消息
        self.message = message
        self.message_start_time = pygame.time.get_ticks()

    def draw_tooltip(self, text, pos):
        """绘制工具提示"""
        padding = 4  # 内边距
        border_radius = 5  # 圆角半径
        shadow_offset = 2  # 阴影偏移
        background_color = (50, 50, 50)  # 背景颜色
        text_color = (255, 255, 255)  # 文本颜色

        # 渲染文本
        tooltip_surface, tooltip_rect = style["font"].render(text, text_color)
        tooltip_rect.topleft = (pos[0] + 20, pos[1])

        # 计算背景大小
        bg_width = tooltip_rect.width + 2 * padding
        bg_height = tooltip_rect.height + 2 * padding

        # 创建一个新的 Surface 对象，用于绘制背景和阴影
        background = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)

        # 绘制阴影
        shadow_rect = pygame.Rect(shadow_offset, shadow_offset, bg_width, bg_height)
        pygame.draw.rect(
            background, (0, 0, 0, 128), shadow_rect, border_radius=border_radius
        )

        # 绘制背景
        pygame.draw.rect(
            background,
            background_color,
            (0, 0, bg_width, bg_height),
            border_radius=border_radius,
        )

        # 先绘制背景和阴影，然后绘制文本
        self.screen.blit(
            background, (tooltip_rect.x - padding, tooltip_rect.y - padding)
        )
        self.screen.blit(tooltip_surface, tooltip_rect)

    def draw_message(self):
        # 绘制当前消息
        if (
            self.message
            and pygame.time.get_ticks() - self.message_start_time
            < self.message_duration
        ):
            # 使用 freetype 字体渲染消息
            message_surface, message_rect = GAME_FONT.render(
                self.message, (255, 255, 255)
            )
            message_rect.center = (
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )

            # 创建阴影效果
            shadow_surface, shadow_rect = GAME_FONT.render(self.message, (0, 0, 0))
            shadow_rect.x = message_rect.x + 2
            shadow_rect.y = message_rect.y + 2

            # 绘制背景矩形
            bg_rect = message_rect.inflate(20, 10)  # 扩大一些以作为背景
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)  # 黑色背景
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)  # 白色边框

            # 首先绘制阴影
            self.screen.blit(shadow_surface, shadow_rect)

            # 绘制消息文本
            self.screen.blit(message_surface, message_rect)
        else:
            self.message = None  # 当消息显示时间结束后清除消息

    def draw_hover_coordinate(
        self, hover_start_time, hover_position, grid_size, font, white
    ):
        # 当鼠标悬停在非 UI 区域超过一定时间时，显示当前坐标
        if hover_position and not self.ui_area.collidepoint(hover_position):
            current_time = pygame.time.get_ticks()
            if (
                hover_start_time is not None and current_time - hover_start_time > 500
            ):  # 悬停超过0.5秒
                x, y = hover_position
                grid_x = (x - self.ui_area.width) // grid_size
                grid_y = y // grid_size
                hover_text = f"({grid_x}, {grid_y})"
                text_surface = font.render(hover_text, True, white)
                self.screen.blit(text_surface, (x + 20, y))  # 将坐标显示在鼠标位置附近


class Map:
    def __init__(self, screen, grid_size, element_images):
        self.screen = screen  # Pygame 屏幕对象，用于绘制地图元素
        self.grid_size = grid_size  # 网格大小，用于计算元素位置
        self.element_images = element_images  # 存储地图元素图像的字典
        self.map_data = {"bricks": [], "irons": []}  # 存储地图元素位置的字典
        self.undo_stack = []  # 撤销操作栈
        self.redo_stack = []  # 重做操作栈

    def draw_elements(self):
        # 绘制地图上的所有元素
        for element_type, positions in self.map_data.items():
            for position in positions:
                element_image = self.element_images.get(element_type)
                if element_image:
                    # 根据元素的位置和网格大小计算其在屏幕上的坐标，并绘制元素图像
                    self.screen.blit(
                        element_image,
                        (
                            # position["x"] * self.grid_size + self.ui.ui_area.width,
                            position["x"] * self.grid_size + 200,
                            position["y"] * self.grid_size,
                        ),
                    )

    def draw_grid(self, ui_width):
        # 绘制地图的网格线
        for x in range(ui_width, self.screen.get_width(), self.grid_size):
            for y in range(0, self.screen.get_height(), self.grid_size):
                # 在每个网格位置绘制矩形框
                pygame.draw.rect(
                    self.screen, grid_color, (x, y, self.grid_size, self.grid_size), 1
                )

    def undo(self):
        # 撤销操作
        if self.undo_stack:
            action, element, position = self.undo_stack.pop()  # 弹出最后一个操作
            if action == "add":
                # 如果操作是添加，则从地图数据中移除该元素，并将其添加到重做栈
                if position in self.map_data[element]:
                    self.map_data[element].remove(position)
                    self.redo_stack.append(("remove", element, position))
            elif action == "remove":
                # 如果操作是移除，则将元素重新添加到地图数据，并将其添加到重做栈
                if position not in self.map_data[element]:
                    self.map_data[element].append(position)
                    self.redo_stack.append(("add", element, position))

    def redo(self):
        # 重做操作
        if self.redo_stack:
            action, element, position = self.redo_stack.pop()
            if action == "add":
                # 如果操作是添加，则将元素添加到地图数据，并将其添加到撤销栈
                if position not in self.map_data[element]:
                    self.map_data[element].append(position)
                    self.undo_stack.append(("remove", element, position))
            elif action == "remove":
                # 如果操作是移除，则从地图数据中移除该元素，并将其添加到撤销栈
                if position in self.map_data[element]:
                    self.map_data[element].remove(position)
                    self.undo_stack.append(("add", element, position))

    def save_map(self, filename):
        # 保存地图数据到文件
        with open(filename, "w") as file:
            json.dump(self.map_data, file, indent=4)  # 将地图数据以 JSON 格式写入文件

    def position_occupied(self, pos, exclude_element=None):
        # 检查指定位置是否被某个元素占用
        for element, positions in self.map_data.items():
            if element != exclude_element and pos in positions:
                return True  # 如果找到占用的元素，则返回 True
        return False  # 如果没有找到占用的元素，则返回 False


class Selection:
    def __init__(self, screen):
        self.screen = screen  # Pygame 屏幕对象，用于绘制选择区域
        self.selection_start = None  # 选择开始时的位置
        self.selection_end = None  # 选择结束时的位置
        self.is_selecting = False  # 当前是否正在选择

    def start_selection(self, position):
        # 开始选择操作
        self.selection_start = position  # 记录选择开始的位置
        self.is_selecting = True  # 设置选择状态为 True

    def update_selection(self, position):
        # 更新选择操作
        self.selection_end = position  # 更新选择结束的位置

    def end_selection(self):
        # 结束选择操作
        self.is_selecting = False  # 设置选择状态为 False
        return self.calculate_selection_rect()  # 返回计算得到的选择区域

    def draw_selection_area(self):
        # 绘制选择区域
        if self.is_selecting and self.selection_start and self.selection_end:
            # 当处于选择状态且已确定开始和结束位置时
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            rect_params = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            # 绘制表示选择区域的矩形框
            pygame.draw.rect(self.screen, selection_color, rect_params, 2)

    def calculate_selection_rect(self):
        # 计算选择区域的矩形
        if self.selection_start and self.selection_end:
            # 确保已经有开始和结束位置
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            # 返回计算得到的矩形区域
            return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        return None


font = pygame.font.Font(None, 36)
grid_size = 24
element_images = {
    "bricks": resource_manager.load_image("brick_image"),
    "irons": resource_manager.load_image("iron_image"),
}
help_text = [
    "H: Hide/Show this help",
    "Click to place or remove an element",
    "U: Undo last action",
    "R: Redo last action",
    "S: Screen shot",
    "Space: Save map",
]


class Map_designer:
    def __init__(self, screen):
        self.screen = screen
        self.game_map = Map(self.screen, grid_size, element_images)
        self.selection = Selection(self.screen)

        self.undo_stack = self.game_map.undo_stack
        self.redo_stack = self.game_map.redo_stack
        self.ui = UI(self.screen, font, self.undo_stack)
        self.current_element = "bricks"
        self.current_mode = "grid"

        # 创建按钮实例
        self.exit_button = Button(10, 250, 170, 30, "Exit")
        self.undo_button = Button(10, 400, 80, 30, "Undo")
        self.redo_button = Button(100, 400, 80, 30, "Redo")
        self.save_button = Button(10, 450, 170, 30, "Save")
        self.screenshot_button = Button(10, 350, 170, 30, "Screenshot")
        self.mode_button = Button(10, 300, 170, 30, "Mode")
        self.bricks_button = Button(10, 10, 180, 30, "Bricks")
        self.irons_button = Button(10, 100, 180, 30, "Irons")
        self.buttons = [
            self.exit_button,
            self.undo_button,
            self.redo_button,
            self.redo_button,
            self.save_button,
            self.screenshot_button,
            self.mode_button,
        ]

        self.show_help = True
        self.running = True
        self.hover_start_time = None
        self.hover_position = None

    def run(self):
        while self.running:
            self.screen.fill(black)
            hover_position = pygame.mouse.get_pos()
            for button in self.buttons:
                button.check_hover(pygame.mouse.get_pos())
                button.update(hover_position)
            self.draw()
            # 更新屏幕显示
            pygame.display.flip()
            self.handle_events()

    def draw(self):
        # 绘制UI和地图
        self.ui.draw_ui(element_images, grey, white)
        if self.current_mode == "grid":
            self.game_map.draw_grid(200)
        self.game_map.draw_elements()
        # 更新选择区域的绘制
        if self.current_mode == "grid":
            self.selection.draw_selection_area()

        # 绘制鼠标悬停坐标
        self.ui.draw_hover_coordinate(
            self.hover_start_time, self.hover_position, grid_size, font, white
        )

        # 更新屏幕显示
        if self.show_help:
            self.ui.draw_help(help_text)

        # 绘制消息
        self.ui.draw_message()
        # 绘制按钮
        for button in self.buttons:
            button.update(pygame.mouse.get_pos())
            button.draw(self.screen)

        # 在所有按钮之后绘制工具提示
        for button in self.buttons:
            if button.is_hovered:
                self.ui.draw_tooltip(f"{button.text} Button", pygame.mouse.get_pos())
                break  # 如果找到一个悬停的按钮，就绘制其工具提示并退出循环

        # 获取鼠标位置并绘制光标
        cursor_rect.topleft = pygame.mouse.get_pos()
        self.screen.blit(cursor_image, cursor_rect)  # 绘制自定义光标

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_sound.play()
                mouse_pos = pygame.mouse.get_pos()

                if self.current_mode == "grid" and not self.ui.ui_area.collidepoint(
                    mouse_pos
                ):
                    grid_x = (mouse_pos[0] - self.ui.ui_area.width) // grid_size
                    grid_y = mouse_pos[1] // grid_size
                    position = {"x": grid_x, "y": grid_y}

                    # 检查该位置是否已被占用
                    if not self.game_map.position_occupied(
                        position, exclude_element=self.current_element
                    ):
                        # 在地图数据中添加或移除元素
                        if position not in self.game_map.map_data[self.current_element]:
                            self.game_map.map_data[self.current_element].append(
                                position
                            )
                            self.game_map.undo_stack.append(
                                ("add", self.current_element, position)
                            )
                        else:
                            self.game_map.map_data[self.current_element].remove(
                                position
                            )
                            self.game_map.undo_stack.append(
                                ("remove", self.current_element, position)
                            )

                    self.selection.start_selection(mouse_pos)

                # 检查是否点击了 UI 区域内的按钮
                if self.ui.ui_area.collidepoint(mouse_pos):
                    # 检查是否点击了元素图标
                    for element, rect in self.ui.icon_rects.items():
                        if rect.collidepoint(mouse_pos):
                            self.current_element = element
                            break

                    if self.undo_button.rect.collidepoint(mouse_pos):
                        # 撤销
                        self.undo_button.handle_click()
                        self.game_map.undo()
                        self.ui.show_message("Undo")
                    elif self.redo_button.rect.collidepoint(mouse_pos):
                        self.redo_button.handle_click()
                        self.game_map.redo()
                        self.ui.show_message("Redo")
                    elif self.save_button.rect.collidepoint(mouse_pos):
                        # 保存地图
                        self.save_button.handle_click()
                        self.game_map.save_map("../maps/self_made_map.json")
                        self.ui.show_message("Map saved")
                    elif self.screenshot_button.rect.collidepoint(mouse_pos):
                        # 截图
                        self.screenshot_button.handle_click()
                        pygame.image.save(self.screen, "../image/screenshot.png")
                        self.ui.show_message("Screenshot saved")
                    elif self.mode_button.rect.collidepoint(mouse_pos):
                        # 切换模式
                        self.mode_button.handle_click()
                        self.current_mode = (
                            "preview" if self.current_mode == "grid" else "grid"
                        )
                        self.ui.show_message(
                            "Preview mode"
                            if self.current_mode == "preview"
                            else "Grid mode"
                        )
                    elif self.exit_button.rect.collidepoint(mouse_pos):
                        self.running = False
                else:
                    # 处理非 UI 区域的点击（如选择区域）
                    if self.current_mode == "grid":
                        self.selection.start_selection(mouse_pos)

            # 处理鼠标释放事件
            if event.type == pygame.MOUSEBUTTONUP:
                if self.current_mode == "grid" and not self.ui.ui_area.collidepoint(
                    pygame.mouse.get_pos()
                ):
                    selected_rect = self.selection.end_selection()
                    # if selected_rect:
                    # print("选择区域:", selected_rect)

            # 处理鼠标移动事件
            if event.type == pygame.MOUSEMOTION:
                self.hover_start_time = pygame.time.get_ticks()
                if self.current_mode == "grid" and not self.ui.ui_area.collidepoint(
                    pygame.mouse.get_pos()
                ):
                    self.selection.update_selection(pygame.mouse.get_pos())

            # 处理键盘事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_u:
                    self.game_map.undo()
                    self.ui.show_message("Undo")
                elif event.key == pygame.K_r:
                    self.game_map.redo()
                    self.ui.show_message("Redo")
                elif event.key == pygame.K_s:
                    pygame.image.save(self.screen, "../image/screenshot.png")
                    self.ui.show_message("Screenshot saved")
                elif event.key == pygame.K_SPACE:
                    self.game_map.save_map("../maps/self_made_map.json")
                    self.ui.show_message("Map saved")


if __name__ == "__main__":
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    designer = Map_designer(screen)
    designer.run()
