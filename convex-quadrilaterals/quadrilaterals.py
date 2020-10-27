from PIL import Image
from random import randint
from itertools import combinations
import os
import math
import numpy

WIDTH = 400
R_POINTS = 3  # must be at least 0

IMG = Image.new('RGB', (WIDTH, WIDTH), (0, 0, 0))


def save_image(filename):
    IMG.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


def plot_point(x, y, color=(255, 255, 0)):
    IMG.putpixel((x, y), color)


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


def draw_point(point, color=(255, 0, 0)):
    draw_circle(point[0], point[1], R_POINTS, color)


def calculate_triangle_area(points):  # (p0, p1, p2)
    return abs(numpy.linalg.det([[1, point[0], point[1]] for point in points]))


def is_inside_triangle(triangle_points, p0):
    total_area = calculate_triangle_area(triangle_points)
    test_area = 0
    for idx in range(len(triangle_points)):
        test_area += calculate_triangle_area(numpy.array(triangle_points[:idx] + triangle_points[idx + 1:] + [p0]))
    return int(round(total_area)) >= int(round(test_area))


def is_convex_quadrilateral(points):  # (p0, p1, p2, p3)
    for idx in range(len(points)):
        if is_inside_triangle(points[:idx] + points[idx + 1:], points[idx]):
            return False
    return True


def calculate_triangle_centroid(points):  # (p0, p1, p2)
    return (sum([point[0] for point in points]) / 3, sum([point[1] for point in points]) / 3)


def calculate_magintude(v):  # calculates the magnitude of the vector v = (a, b, c, ...)
    return math.sqrt(sum([n ** 2 for n in v]))


def calculate_distance(p0, p1):
    return calculate_magintude(((p1[0] - p0[0]), (p1[1] - p0[1])))


def calculate_centroid(arr):
    length = arr.shape[0]
    sum_x = numpy.sum(arr[:, 0])
    sum_y = numpy.sum(arr[:, 1])
    return sum_x/length, sum_y/length


triangular_area = 0
while triangular_area == 0:  # loops while points are colinear by checking the area of the triangle the points form
    points = numpy.array(sorted((randint(R_POINTS, WIDTH - R_POINTS - 1), randint(R_POINTS, WIDTH - R_POINTS - 1)) for i in range(3)))
    triangular_area = calculate_triangle_area(points)

fourth_point = points[0]  # guarantees point is inside triangle
while not is_convex_quadrilateral([tuple(point) for point in points] + [tuple(fourth_point)]):
    fourth_point = (randint(R_POINTS, WIDTH - R_POINTS - 1), randint(R_POINTS, WIDTH - R_POINTS - 1))
points = numpy.append(points, [fourth_point], axis=0)

for point in points:
    draw_point(point)

centroid = tuple([int(n) for n in calculate_centroid(points)])
print('Centroid: {}'.format(centroid))
draw_point(centroid, (0, 255, 255))

points = numpy.array([elem[1] for elem in sorted([(math.atan2(point[1] - centroid[1], point[0] - centroid[0]), point) for point in points])])

print('Endpoints (sorted): {}'.format(points))
for idx in range(len(points)):
    draw_line(points[idx], points[(idx + 1) % 4])

save_image('quadrilateral.png')
