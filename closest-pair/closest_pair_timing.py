from PIL import Image
from random import shuffle, random
from itertools import combinations
from time import time
import os
import math
import numpy
import sys

WIDTH = 10000
R_POINTS = 3  # must be at least 0

IMG = Image.new('RGB', (WIDTH, WIDTH), (0, 0, 0))


def adj_sig_figs(n, x):  # truncate the number x to have n significant figures
    if not x:
        return 0
    dec = int(math.log10(abs(x)) // 1)
    z = int((x * 10 ** (n - 1 - dec) + 0.5) // 1) / 10 ** (n - 1 - dec)
    return str(z) if z % 1 else str(int(z))


def calculate_magintude(v):  # calculates the magnitude of the vector v = (a, b, c, ...)
    return math.sqrt(sum([n ** 2 for n in v]))


def calculate_distance(p0, p1):
    return calculate_magintude(((p1[0] - p0[0]), (p1[1] - p0[1])))


def generate_random_points(count):
    return sorted((random() * WIDTH, random() * WIDTH) for _ in range(count))


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


def randomized(unshuffled):  # is not perfect (only an estimate), use recursive for 100% accuracy
    points = unshuffled.copy()
    shuffle(points)
    best_pair = (points[0], points[1])
    delta = calculate_distance(points[0], points[1])
    half_delta = delta / 2
    grid_dictionary = {}
    for idx, point in enumerate(points):
        i = int(round(point[0] / half_delta))
        j = int(round(point[1] / half_delta))
        if i in grid_dictionary and j in grid_dictionary[i]:
            subsquare = grid_dictionary[i][j]
        else:
            subsquare = set()
            for i_current in range(i - 2, i + 2):
                for j_current in range(j - 2, j + 2):
                    if not (i_current == i and j_current == j) and i_current in grid_dictionary and j_current in grid_dictionary[i_current]:
                        subsquare |= grid_dictionary[i_current][j_current]
            if not subsquare:
                if not i in grid_dictionary:
                    grid_dictionary[i] = {}
                if not j in grid_dictionary[i]:
                    grid_dictionary[i][j] = set()
                grid_dictionary[i][j].add(point)
                continue
        create_new_dictionary = False
        for other_point in subsquare:
            distance = calculate_distance(point, other_point)
            if distance < delta:
                best_pair = (point, other_point)
                delta = distance
                if delta == 0:
                    break
                half_delta = delta / 2
                create_new_dictionary = True
        if create_new_dictionary:
            grid_dictionary = {}
            for p in points[:idx+1]:
                i_current = int(round(p[0] / half_delta))
                if not i_current in grid_dictionary:
                    grid_dictionary[i_current] = {}
                j_current = int(round(p[1] / half_delta))
                if not j_current in grid_dictionary[i_current]:
                    grid_dictionary[i_current][j_current] = set()
                grid_dictionary[i_current][j_current].add(p)
    return (calculate_distance(best_pair[0], best_pair[1]), best_pair[0], best_pair[1])


for trial_count in [100, 1000, 10000, 100000, 1000000]:
    points = generate_random_points(trial_count)
    t = time()
    brute_force(points)
    t_brute_force = time() - t
    t = time()
    recursive(points)
    t_recursive = time() - t
    t = time()
    randomized(points)
    t_randomized = time() - t
    print()
    
    print('TRIAL COUNT: {} POINTS'.format(trial_count))
    print('----------------------')
    print('Brute force => {}s'.format(adj_sig_figs(3, t_brute_force)))
    print('Recursive => {}s'.format(adj_sig_figs(3, t_recursive)))
    print('Randomized => {}s'.format(adj_sig_figs(3, t_randomized)))
    print('----------------------')
