from PIL import Image
from random import randint
from itertools import combinations
import os
import math

WIDTH = 400
VERTICES = 3

IMG = Image.new('RGB', (WIDTH, WIDTH), (0, 0, 0))


def save_image(filename):
    IMG.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


def plot_point(p, inverse=False):
    if inverse:
        p = (p[1], p[0])
    IMG.putpixel((p[0], p[1]), (255, 255, 0))
    return p


def draw_line(p1, p2):
    x1, x2, y1, y2 = p1[0], p2[0], p1[1], p2[1]
    if x1 > x2:
        x2, x1, y2, y1, p2, p1 = x1, x2, y1, y2, p1, p2
    x_reflect, y_reflect = None, None
    if y1 > y2:
        y2, y1 = y1, y2
        x_reflect = math.ceil((x1 + x2) / 2)
    dx = x2 - x1
    dy = y2 - y1
    if dx and dy / dx > 1:
        inverse = True
        y1, y2, x1, x2, dy, dx = x1, x2, y1, y2, dx, dy
        if x_reflect:
            x_reflect = None
            y_reflect = int(((y1 + y2) / 2) + 0.5)
    else:
        inverse = False
    difference = dy * 2 - dx
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        p = (x_reflect * 2 - x if x_reflect else x, y_reflect * 2 - y if y_reflect else y)
        if inverse:
            points.append((p[1], p[0]))
        else:
            points.append(p)
        if difference > 0:
            y += 1
            difference -= dx * 2
        difference += dy * 2
    if p1 == (points[-1][0] - 1, points[-1][1]):
        for idx, p in enumerate(points):
            points[idx] = (p[0] - 1, p[1])
    for point in points:
        plot_point(point)


points = [(randint(0, WIDTH - 1), randint(0, WIDTH - 1)) for i in range(VERTICES)]
print(sorted(points))

for endpoints in combinations(points, 2):
    draw_line(endpoints[0], endpoints[1])

save_image('triangle.png')
