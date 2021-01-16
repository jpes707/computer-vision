from PIL import Image
import urllib.request
from time import time
import io
import ssl
import sys
import random
import math
import os
import atexit

K_MEANS_TRIALS = 1


def adj_sig_figs(n, x):  # truncate the number x to have n significant figures
    if not x:
        return 0
    dec = int(math.log10(abs(x)) // 1)
    z = int((x * 10 ** (n - 1 - dec) + 0.5) // 1) / 10 ** (n - 1 - dec)
    return str(z) if z % 1 else str(int(z))


k = int(sys.argv[1])

if sys.argv[2][:4] == 'http':
    #ssl._create_default_https_context = ssl._create_unverified_context
    img = Image.open(io.BytesIO(urllib.request.urlopen(str(sys.argv[2])).read())).convert('RGB')
else:
    img = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[2])).convert('RGB')

start_time = time()

print('Size: {} x {}'.format(img.size[0], img.size[1]))
print('Pixels: {}'.format(img.size[0] * img.size[1]))
#sys.setrecursionlimit(img.size[0] * img.size[1] + 1)

pixel_dictionary = {}
pix = img.load()
for x in range(img.size[0]):
    for y in range(img.size[1]):
        if pix[x, y] in pixel_dictionary:
            pixel_dictionary[pix[x, y]] += 1
        else:
            pixel_dictionary[pix[x, y]] = 1
print('Distinct pixel count: {}'.format(len(pixel_dictionary)))
reversed_dictionary = dict(map(reversed, pixel_dictionary.items()))
reversed_key = max(reversed_dictionary)
print('Most common pixel: {} => {}'.format(reversed_dictionary[reversed_key], reversed_key))


def run_k_means(k, pixel_weights):
    min_variance = float('inf')
    pixel_list = []
    for pixel in sorted(pixel_dictionary):
        pixel_list += [pixel] * pixel_dictionary[pixel]
    for _ in range(K_MEANS_TRIALS):
        # print('on pass', i)
        means_set, pixel_mapping, iteration_count, old_means_set = single_k_means(k, pixel_list, pixel_weights)
        variance = calculate_variance(k, pixel_mapping)
        if variance < min_variance:
            min_variance = variance
            best_means_set = means_set
            best_pixel_mapping = pixel_mapping
            best_iteration_count = iteration_count
            best_old_means_set = old_means_set
    return best_means_set, best_pixel_mapping, best_iteration_count, best_old_means_set


def single_k_means(k, pixel_list, pixel_weights):
    means_set = []
    for i in range(k):
        new_pixel = pixel_list[random.randint(0, len(pixel_list) - 1)]  # (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        while new_pixel in means_set:
            new_pixel = pixel_list[random.randint(0, len(pixel_list) - 1)]
        means_set.append(new_pixel)
    original_means_set = means_set
    pixel_mapping = {}
    for pixel in pixel_weights:
        min_distance = float('inf')
        best_mean = ()
        for mean in means_set:
            distance = calculate_distance(pixel, mean)
            if distance < min_distance:
                min_distance = distance
                best_mean = mean
        pixel_mapping[pixel] = best_mean
    old_pixel_mapping = pixel_mapping.copy()
    pixel_mapping = {}
    iterations = 0
    while True:
        means_average_dictionary = {mean: [[0, 0, 0], 0] for mean in means_set}  # [list sum of (x, y, z) for each pixel that has the mean, number of pixels that have the mean]
        for pixel in pixel_weights:
            current_mean = old_pixel_mapping[pixel]
            pixel_count = pixel_weights[pixel]
            for i in range(3):
                means_average_dictionary[current_mean][0][i] += pixel[i] * pixel_count
            means_average_dictionary[current_mean][1] += pixel_count
        means_set = []
        for mean in means_average_dictionary:
            means_set.append(tuple([int(means_average_dictionary[mean][0][i] / means_average_dictionary[mean][1]) for i in range(3)]))
        for pixel in pixel_weights:
            min_distance = float('inf')
            best_mean = ()
            for mean in means_set:
                distance = calculate_distance(pixel, mean)
                if distance < min_distance:
                    min_distance = distance
                    best_mean = mean
            pixel_mapping[pixel] = best_mean
        if pixel_mapping == old_pixel_mapping:
            return means_set, pixel_mapping, iterations, original_means_set
        old_pixel_mapping = pixel_mapping.copy()
        pixel_mapping = {}
        iterations += 1


def calculate_variance(k, pixel_mapping):
    variance = 0
    for pixel in pixel_mapping:
        variance += calculate_distance(pixel, pixel_mapping[pixel])
    return variance


def calculate_distance(c1, c2):
    p = 0
    for i in range(3):
        p += (c2[i] - c1[i]) ** 2
    return math.sqrt(p)


means_set, pixel_mapping, iteration_count, old_means_set = run_k_means(k, pixel_dictionary)
for x in range(img.size[0]):
    for y in range(img.size[1]):
        pix[x, y] = pixel_mapping[pix[x, y]]
sum_by_means = {mean: 0 for mean in means_set}
# img.show()
for x in range(img.size[0]):
    for y in range(img.size[1]):
        sum_by_means[pix[x, y]] += 1
print('Original means => final means => pixel counts:')
for idx, tup in enumerate(sorted([(sum_by_means[mean], mean, old_means_set[mean_idx]) for mean_idx, mean in enumerate(means_set)], reverse=True)):
    print('{}: {} => {} => {}'.format(idx + 1, tup[2], tup[1], tup[0]))
img.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output.jpg'))

elapsed_time = time() - start_time
print('Time elapsed: {} seconds'.format(adj_sig_figs(3, elapsed_time)))
print('Number of steps: {} steps'.format(iteration_count))
print('Rough time per step: {} steps/second'.format(adj_sig_figs(3, iteration_count / elapsed_time)))
