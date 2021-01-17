from PIL import Image
from random import randint
from itertools import combinations
from time import time
from random import shuffle
import os
import math
import numpy
import sys

WIDTH = 10000
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
    return sorted((randint(R_POINTS, WIDTH - R_POINTS - 1), randint(R_POINTS, WIDTH - R_POINTS - 1)) for _ in range(count))


def brute_force(points):
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
    return (min_distance, min_p0, min_p1)


def split_brute_force(points_first, points_second):  # uses brute force to find the minimum distance between points where one point is in points_first and the other is in points_second
    min_distance = WIDTH ** 2
    min_p0 = None
    min_p1 = None
    for p0 in points_first:
        for p1 in points_second:
            distance = calculate_distance(p0, p1)
            if distance < min_distance:
                min_distance = distance
                min_p0 = p0
                min_p1 = p1
    return (min_distance, min_p0, min_p1)


def recursive(points, use_x=True):
    points_len = len(points)
    if points_len <= 50:
        return brute_force(points)
    dimension_index = 0 if use_x else 1
    points = sorted(points, key=lambda p:p[dimension_index])
    points_halfway = int(points_len / 2)
    points_first = points[:points_halfway]
    min_points_first = recursive(points_first, not use_x)
    points_second = points[points_halfway:]
    min_points_second = recursive(points_second, not use_x)
    min_of_halves = min(min_points_first, min_points_second)
    lower_bound = points_second[0][dimension_index] - min_of_halves[0]
    for lower_idx in range(len(points_first) - 1, -1, -1):
        if points_first[lower_idx][dimension_index] < lower_bound:
            break
    lower_idx += 1
    points_first_brute_force = points_first[lower_idx:]
    upper_bound = points_first[-1][dimension_index] + min_of_halves[0]
    for upper_idx in range(len(points_second)):
        if points_second[upper_idx][dimension_index] > upper_bound:
            break
    points_second_brute_force = points_second[:upper_idx]
    min_split_points = split_brute_force(points_first_brute_force, points_second_brute_force)
    return min(min_points_first, min_points_second, min_split_points)


def new_grid_dictionary(half_delta):
    current_width = 0
    while current_width < WIDTH:
        current_width += half_delta
    num_squares_per_row = int(current_width / half_delta)
    blank_dictionary = [[set() for j in range(num_squares_per_row)] for i in range(num_squares_per_row)]
    return blank_dictionary, num_squares_per_row


def randomized(unshuffled):
    points = unshuffled.copy()
    shuffle(points)
    best_pair = (points[0], points[1])
    delta = calculate_distance(points[0], points[1])
    half_delta = int(round(delta / 2))
    grid_dictionary, num_squares_per_row = new_grid_dictionary(half_delta)
    for idx, point in enumerate(points):
        i = point[0] // half_delta
        j = point[1] // half_delta
        subsquare = grid_dictionary[i][j]
        if not subsquare:
            subsquare = set()
            for i_current in range(i - 2, i + 2):
                for j_current in range(j - 2, j + 2):
                    if not (i_current == i and j_current == j) and i_current < num_squares_per_row and j_current < num_squares_per_row:
                        subsquare |= grid_dictionary[i_current][j_current]
            if not subsquare:
                grid_dictionary[i][j].add(point)
                continue
        create_new_dictionary = False
        for other_point in subsquare:
            distance = calculate_distance(point, other_point)
            if distance < delta:
                best_pair = (point, other_point)
                delta = distance
                create_new_dictionary = True
        if create_new_dictionary:
            print(idx, 'new dict')
            half_delta = int(round(delta / 2))
            grid_dictionary, num_squares_per_row = new_grid_dictionary(half_delta)
            for p in points[:idx+1]:
                i_current = p[0] // half_delta
                j_current = p[1] // half_delta
                grid_dictionary[i_current][j_current].add(p)
    return (calculate_distance(best_pair[0], best_pair[1]), best_pair[0], best_pair[1])


points = generate_random_points(10000)
# t = time()
# print(brute_force(points))
# print(time() - t)
t = time()
print(recursive(points))
print(time() - t)
t = time()
print(randomized(points))
print(time() - t)
