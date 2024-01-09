import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw
from utilise import change_image

# Create a 25x25 -sized image
w, h = 25, 25
image = Image.new('RGB', (w, h), color='white')
draw = ImageDraw.Draw(image)

# offset color：white
color_matrix = [['#FFFFFF' for _ in range(w)] for _ in range(h)]

# 创建Tkinter窗口
window = tk.Tk()
window.geometry('800x800')
window.title('RGB 编辑器')

canvas = tk.Canvas(window, width=w*25, height=h*25, bg='white')
canvas.pack()

def draw_canvas():
    for i in range(w):
        for j in range(h):
            color = color_matrix[j][i]
            canvas.create_rectangle(i*25, j*25, (i+1)*25, (j+1)*25, fill=color, outline="")

draw_canvas()

def update_color(event):
    i, j = event.x//25, event.y//25
    color = simpledialog.askstring("输入颜色", "请输入#abcdef形式的颜色值：")
    try:
        if len(color) != 7 or not all(c in '0123456789abcdefABCDEF' for c in color[1:]):
            raise ValueError
        color_matrix[j][i] = color
        draw.rectangle([i, j, i+1, j+1], fill=color)
        draw_canvas()
    except ValueError:
        messagebox.showerror("错误", "颜色值格式错误！")

canvas.bind("<Button-1>", update_color)

def export_data():
    new_window = tk.Toplevel()
    text = tk.Text(new_window)
    text.pack()
    for row in color_matrix:
        text.insert('end', str(row) + '\n')

def generate_bullet_images():
    # create a bullet upward
    bullet_up = image

    # downward
    bullet_down = (image, "down")

    # left
    bullet_left = change_image(image, "left")

    # right
    bullet_right = change_image(image, "right")

    # save photos for user-defined bullet
    bullet_up.save("../image/user_bullet_up.png")
    bullet_down.save("../image/user_bullet_down.png")
    bullet_left.save("../image/user_bullet_left.png")
    bullet_right.save("../image/user_bullet_right.png")

tk.Button(window, text='导出数据', command=export_data).pack()
tk.Button(window, text='生成子弹图片', command=generate_bullet_images).pack()

# begin tkinter mainloop
window.mainloop()