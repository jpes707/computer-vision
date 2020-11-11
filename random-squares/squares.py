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


def calculate_centroid(points):
    length = points.shape[0]
    sum_x = numpy.sum(points[:, 0])
    sum_y = numpy.sum(points[:, 1])
    return sum_x/length, sum_y/length


def calculate_four_points_intersection(points):  # (p0, p1, p2, p3), p0 and p1 are on L0, p2 and p3 are on L1
    x = [point[0] for point in points]
    y = [point[1] for point in points]
    t_numerator = float((x[0] - x[2]) * (y[2] - y[3]) - (y[0] - y[2]) * (x[2] - x[3]))
    t_denominator = float((x[0] - x[1]) * (y[2] - y[3]) - (y[0] - y[1]) * (x[2] - x[3]))
    t = t_numerator / t_denominator
    return (x[0] + t * (x[1] - x[0]), y[0] + t * (y[1] - y[0]))


def calculate_point_distance_to_line(points):  # (p0, p1, p2), p0 and p1 form the line, p2 is the lone point
    return abs((points[2][0]-points[1][0])*(points[1][1]-points[0][1]) - (points[1][0]-points[0][0])*(points[2][1]-points[1][1])) / numpy.sqrt(numpy.square(points[2][0]-points[1][0]) + numpy.square(points[2][1]-points[1][1]))


def calculate_closest_point_on_line(points):  # (p0, p1, p2), p0 and p1 form the line, p2 is the lone point
    dx, dy = points[1][0]-points[0][0], points[1][1]-points[0][1]
    det = dx * dx + dy * dy
    m = (dy * (points[2][1] - points[0][1]) + dx * (points[2][0] - points[0][0])) / det
    return (int(points[0][0] + m * dx), int(points[0][1] + m * dy))


def calculate_point_in_vector_direction(vector_start_point, vector_end_point, units_away):
    magnitude = calculate_distance(vector_start_point, vector_end_point)
    t = units_away / magnitude
    return (int(round((1 - t) * vector_start_point[0] + t * vector_end_point[0])), int(round((1 - t) * vector_start_point[1] + t * vector_end_point[1])))


def generate_convex_quadrilateral_points():
    triangular_area = 0
    while triangular_area == 0:  # loops while points are colinear by checking the area of the triangle the points form
        points = numpy.array(sorted((randint(R_POINTS, WIDTH - R_POINTS - 1), randint(R_POINTS, WIDTH - R_POINTS - 1)) for i in range(3)))
        triangular_area = calculate_triangle_area(points)
    fourth_point = points[0]  # guarantees point is inside triangle
    while not is_convex_quadrilateral([tuple(point) for point in points] + [tuple(fourth_point)]):
        fourth_point = (randint(R_POINTS, WIDTH - R_POINTS - 1), randint(R_POINTS, WIDTH - R_POINTS - 1))
    return numpy.append(points, [fourth_point], axis=0)


def attempt_draw_square(points):
    centroid = tuple([int(n) for n in calculate_centroid(points)])
    # print('Centroid: {}'.format(centroid))

    points = numpy.array([elem[1] for elem in sorted([(math.atan2(point[1] - centroid[1], point[0] - centroid[0]), point) for point in points])])

    # print('Endpoints (sorted): {}'.format(points))
    for idx in range(len(points)):
        draw_line(points[idx], points[(idx + 1) % 4])

    if calculate_distance(points[0], points[2]) < calculate_distance(points[1], points[3]):
        shortest_slice = [tuple(points[0]), tuple(points[2])]
        if calculate_point_distance_to_line(shortest_slice + [points[1]]) < calculate_point_distance_to_line(shortest_slice + [points[3]]):
            closest_vertex = points[1]
            farthest_vertex = points[3]
        else:
            closest_vertex = points[3]
            farthest_vertex = points[1]
    else:
        shortest_slice = [tuple(points[1]), tuple(points[3])]
        if calculate_point_distance_to_line(shortest_slice + [points[0]]) < calculate_point_distance_to_line(shortest_slice + [points[2]]):
            closest_vertex = points[0]
            farthest_vertex = points[2]
        else:
            closest_vertex = points[2]
            farthest_vertex = points[0]

    draw_line(shortest_slice[0], shortest_slice[1], (255, 0, 255))
    closest_point_on_slice = calculate_closest_point_on_line(shortest_slice + [closest_vertex])
    draw_line(closest_point_on_slice, closest_vertex, (255, 0, 255))
    first_point_on_square = calculate_closest_point_on_line([closest_vertex, closest_point_on_slice, farthest_vertex])
    draw_line(first_point_on_square, closest_vertex, (255, 0, 255))
    side_length = calculate_distance(first_point_on_square, closest_point_on_slice)
    third_square_vertex = calculate_point_in_vector_direction(first_point_on_square, farthest_vertex, side_length)
    fourth_square_vertex = calculate_closest_point_on_line((closest_point_on_slice, shortest_slice[1], third_square_vertex))

    square_vertices = [closest_point_on_slice, first_point_on_square, third_square_vertex, fourth_square_vertex]
    for idx in range(4):
        draw_point(square_vertices[idx], (0, 255, 0))
        draw_line(square_vertices[idx], square_vertices[(idx + 1) % 4], (0, 255, 255))
    
    for point in points:
        draw_point(point)

if len(sys.argv) > 1:
    points_read = [int(round(float(endpoint) * WIDTH)) for line in open(get_relative_path(sys.argv[1]), 'r').readlines()[:4] for endpoint in line[:-1].split(' ')]
    points = numpy.array([[points_read[idx], points_read[idx + 1]] for idx in range(0, len(points_read), 2)])
else:
    points = generate_convex_quadrilateral_points()

while True:
    try:
        attempt_draw_square(points)
        break
    except:
        IMG = Image.new('RGB', (WIDTH, WIDTH), (0, 0, 0))
        points = generate_convex_quadrilateral_points()

save_image('square.png')
