from PIL import Image
from random import randint
from itertools import combinations
import os
import math
import numpy
import sys

WIDTH = 400
R_POINTS = 3  # must be at least 0

IMG = Image.new('RGB', (WIDTH, WIDTH), (0, 0, 0))


class CustomError(Exception):
    pass


def get_relative_path(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)


def save_image(filename):
    IMG.save(get_relative_path(filename))


def plot_point(x, y, color=(255, 255, 0)):
    if x < 0 or y < 0:
        raise CustomError('Graphing of negative point attempted')
    IMG.putpixel((x, y), color)


def draw_line(p1, p2, color=(255, 255, 0)):
    x1, x2, y1, y2 = p1[0], p2[0], p1[1], p2[1]
    if x1 >= x2:
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


def draw_point(point, color=(255, 0, 0)):
    draw_circle(point[0], point[1], R_POINTS, color)


def calculate_magintude(v):  # calculates the magnitude of the vector v = (a, b, c, ...)
    return math.sqrt(sum([n ** 2 for n in v]))


def calculate_distance(p0, p1):
    return calculate_magintude(((p1[0] - p0[0]), (p1[1] - p0[1])))


def generate_random_points(count):
    return numpy.array(sorted((randint(R_POINTS, WIDTH - R_POINTS - 1), randint(R_POINTS, WIDTH - R_POINTS - 1)) for _ in range(count)))


if len(sys.argv) > 1:
    points_read = [int(R_POINTS + round(float(endpoint) * (WIDTH - 2 * R_POINTS))) for line in open(get_relative_path(sys.argv[1]), 'r').readlines() for endpoint in line[:-1].split(' ')]
    points = numpy.array([[points_read[idx], points_read[idx + 1]] for idx in range(0, len(points_read), 2)])
else:
    points = generate_random_points(int(sys.argv[2]) if len(sys.argv) > 2 else 50)

for point in points:
    draw_point(point)

min_distance = WIDTH ** 2
min_p0 = None
min_p1 = None
for idx, p0 in enumerate(points):
    for p1 in points[idx + 1:]:
        distance = calculate_distance(p0, p1)
        if distance < min_distance:
            min_distance = distance
            min_p0 = p0
            min_p1 = p1
draw_point(min_p0, (255, 255, 0))
draw_point(min_p1, (255, 255, 0))

save_image('closest_pair.png')
