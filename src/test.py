import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置窗口大小
window_size = (400, 300)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("键盘按键检测")

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 检测键盘按键
        elif event.type == pygame.KEYDOWN:
            print("按下键盘按键:", pygame.key.name(event.key))

        elif event.type == pygame.KEYUP:
            print("释放键盘按键:", pygame.key.name(event.key))

    # 更新屏幕
    pygame.display.flip()

# 退出程序
pygame.quit()
