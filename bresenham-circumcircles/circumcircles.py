from PIL import Image
from random import randint
from itertools import combinations
import os
import math
import numpy

WIDTH = 400
VERTICES = 3

IMG = Image.new('RGB', (WIDTH, WIDTH), (0, 0, 0))


def save_image(filename):
    IMG.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


def plot_point(p1, p2, color=(255, 255, 0)):
    IMG.putpixel((p1, p2), color)


def draw_line(p1, p2, color=(255, 255, 0)):
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
    if numpy.array_equal(p1, [points[-1][0] - 1, points[-1][1]]):
        for idx, p in enumerate(points):
            points[idx] = (p[0] - 1, p[1])
    for point in points:
        plot_point(point[0], point[1], color)


def draw_circle(x0, y0, r, color=(255, 0, 0)):
    x = 0
    dx = 1
    dy = -2 * r
    y = r
    h = 1 - r
    while x < y:
        x += 1
        dx += 2
        h += dx
        if h >= 0:
            dy += 2
            h += dy
            y -= 1
        plot_point(x0 + y, y0 + x, color)
        plot_point(x0 - y, y0 + x, color)
        plot_point(x0 + y, y0 - x, color)
        plot_point(x0 - y, y0 - x, color)
        plot_point(x0 + x, y0 + y, color)
        plot_point(x0 - x, y0 + y, color)
        plot_point(x0 + x, y0 - y, color)
        plot_point(x0 - x, y0 - y, color)
    plot_point(x0, y0 + r, color)
    plot_point(x0, y0 - r, color)
    plot_point(x0 + r, y0, color)
    plot_point(x0 - r, y0, color)


x0, y0, r = 0, 0, 1
while x0 - r < 0 or x0 + r >= WIDTH or y0 - r < 0 or y0 + r >= WIDTH:
    points = numpy.array(sorted((randint(0, WIDTH - 1), randint(0, WIDTH - 1)) for i in range(VERTICES)))

    a = int(numpy.linalg.det([[point[0], point[1], 1] for point in points]))
    bx = -int(numpy.linalg.det([[point[0] ** 2 + point[1] ** 2, point[1], 1] for point in points]))
    by = int(numpy.linalg.det([[point[0] ** 2 + point[1] ** 2, point[0], 1] for point in points]))
    c = -int(numpy.linalg.det([[point[0] ** 2 + point[1] ** 2, point[0], point[1]] for point in points]))

    if a != 0:
        x0 = int(round(-bx / (2 * a)))
        y0 = int(round(-by / (2 * a)))
        r = int(round(math.sqrt(bx ** 2 + by ** 2 - 4 * a * c) / (2 * abs(a))))

print('Triangle endpoints: {}'.format(points))
print('Circle: (x - {})^2 + (y - {})^2 = {}^2'.format(x0, y0, r))

for endpoints in combinations(points, 2):
    draw_line(endpoints[0], endpoints[1])
draw_circle(x0, y0, r)

save_image('circumcircle.png')
