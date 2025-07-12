import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))
from PIL import Image, ImageDraw, ImageFont

from fcntl import ioctl
import mmap

fb: any
mm: any
screen_width = 640
screen_height = 480
bytes_per_pixel = 4
screen_size = screen_width * screen_height * bytes_per_pixel

fontFile = {}
fontFile[15] = ImageFont.truetype("/mnt/mmc/MUOS/application/ROMDownloader/App/font/Lexend-Regular.ttf", 17)
fontFile[13] = ImageFont.truetype("/mnt/mmc/MUOS/application/ROMDownloader/App/font/Lexend-Regular.ttf", 15)
fontFile[11] = ImageFont.truetype("/mnt/mmc/MUOS/application/ROMDownloader/App/font/Lexend-Regular.ttf", 13)
colorBlue = "#bb7200"
colorBlueD1 = "#7f4f00"
colorGray = "#292929"
colorGrayL1 = "#383838"
colorGrayD2 = "#141414"

activeImage: Image.Image
activeDraw: ImageDraw.ImageDraw

def screen_reset():
	ioctl(fb, 0x4601, b'\x80\x02\x00\x00\xe0\x01\x00\x00\x80\x02\x00\x00\xc0\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00^\x00\x00\x00\x96\x00\x00\x00\x00\x00\x00\x00\xc2\xa2\x00\x00\x1a\x00\x00\x00T\x00\x00\x00\x0c\x00\x00\x00\x1e\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
	ioctl(fb, 0x4611, 0)

def draw_start():
	global fb, mm
	fb = os.open('/dev/fb0', os.O_RDWR)
	mm = mmap.mmap(fb, screen_size)

def draw_end():
	global fb, mm
	mm.close()
	os.close(fb)

def crate_image():
	image = Image.new('RGBA', (screen_width, screen_height), color='black')
	return image

def draw_active(image):
	global activeImage, activeDraw
	activeImage = image
	activeDraw = ImageDraw.Draw(activeImage)

def draw_paint():
	global activeImage
	mm.seek(0)
	mm.write(activeImage.tobytes())

def draw_clear():
	global activeDraw
	activeDraw.rectangle([0, 0, screen_width, screen_height], fill='black')

def draw_text(position, text, font=15, color='white', **kwargs):
	global activeDraw
	activeDraw.text(position, text, font=fontFile[font], fill=color, **kwargs)

def draw_rectangle(position, fill=None, outline=None, width=1):
	global activeDraw
	activeDraw.rectangle(position, fill=fill, outline=outline, width=width)

def draw_rectangle_r(position, radius, fill=None, outline=None):
	global activeDraw
	activeDraw.rounded_rectangle(position, radius, fill=fill, outline=outline)

def draw_circle(position, radius, fill=None, outline='white'):
	global activeDraw
	activeDraw.ellipse([position[0]-radius, position[1]-radius, position[0]+radius, position[1]+radius], fill=fill, outline=outline)

def row_list(text, pos, width, selected):
    fill_color = colorBlue if selected else colorGrayL1
    draw_rectangle_r([pos[0], pos[1], pos[0]+width, pos[1]+32], 5, fill=fill_color)
    draw_text((pos[0]+5, pos[1] + 5), text)

def button_circle(pos, button, text):
	draw_circle(pos, 15, fill=colorBlueD1, outline=None)
	draw_text(pos, button, anchor="mm")
	draw_text((pos[0] + 20, pos[1]), text, font=13, anchor="lm")

def draw_log(text, fill="Black", outline="black"):
    rect_x0, rect_y0, rect_x1, rect_y1 = 170, 200, 470, 280
    max_width = rect_x1 - rect_x0 - 20  # márgenes internos
    font = fontFile[15]

    # Intentar dividir el texto si es muy ancho
    text_lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        test_width, _ = font.getsize(test_line)
        if test_width <= max_width:
            line = test_line
        else:
            text_lines.append(line)
            line = word

    text_lines.append(line)  # Añadir la última línea

    # Si hay más de dos líneas, juntar todo en dos como máximo
    if len(text_lines) > 2:
        first_line = ' '.join(words[:len(words)//2])
        second_line = ' '.join(words[len(words)//2:])
        text_lines = [first_line, second_line]

    # Calcular el alto total del bloque de texto
    total_height = len(text_lines) * font.getsize("A")[1] + (len(text_lines) - 1) * 5

    # Dibujar el rectángulo
    draw_rectangle_r([rect_x0, rect_y0, rect_x1, rect_y1], 5, fill=fill, outline=outline)

    # Dibujar las líneas centradas
    rect_center_x = (rect_x0 + rect_x1) // 2
    start_y = (rect_y0 + rect_y1) // 2 - total_height // 2

    for i, line in enumerate(text_lines):
        text_width, text_height = font.getsize(line)
        text_x = rect_center_x - text_width // 2
        text_y = start_y + i * (text_height + 5)
        draw_text((text_x, text_y), line)


draw_start()
screen_reset()

imgMain = crate_image()
draw_active(imgMain)
