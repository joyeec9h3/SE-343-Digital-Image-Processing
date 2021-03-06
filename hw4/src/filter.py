#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Spatial filters."""

import numpy as np

from util import img_to_array, array_to_img
from math import floor, ceil


def filter2d(input_img, filter):
    """Apply a 2-d filter to a 2-d image."""
    M, N = input_img.shape  # M is height, N is width
    n, m = len(filter), len(filter[0])  # m is height, n is width
    a, b = m / 2, n / 2  # size of neighborhood

    # get transpose of the 1-d filter
    if isinstance(filter, np.ndarray):
        wt = filter.ravel()
    else:
        wt = np.array(filter).ravel()

    def correlate(x, y):
        # z = np.zeros(n * m)  # pad with zeros
        z = np.full(n * m, input_img[x, y])  # pad with border duplicates
        # fill in available neighborhood
        for i in xrange(x - a, x + a + 1):
            for j in xrange(y - b, y + b + 1):
                if i >= 0 and i < M and j >= 0 and j < N:
                    z[(i - x + a) * n + j - y + b] = input_img[i, j]
        return np.dot(wt, z)

    # apply to each pixel
    xx, yy = np.meshgrid(xrange(M), xrange(N), indexing='ij')
    vf = np.vectorize(correlate)
    return vf(xx, yy)


def arithmetic_mean(img, size, raw=False):
    """Smooth the given image with arithmetic mean filter of given size."""
    m, n = size
    kernel = np.full((m, n), float(1) / (m * n))  # denominator
    data = img if raw else img_to_array(img)

    if raw:
        return filter2d(data, kernel)
    else:
        return array_to_img(filter2d(data, kernel), img.mode)


def harmonic_mean(img, size):
    """Smooth the given image with harmonic mean filter of given size."""
    data = img_to_array(img, dtype=np.float64)
    inverse = np.reciprocal(data)
    result = np.reciprocal(arithmetic_mean(inverse, size, True))
    return array_to_img(result, img.mode)


def contraharmonic_mean(img, size, Q):
    """Smooth the given image with contraharmonic mean filter
       of given size and Q."""
    data = img_to_array(img, dtype=np.float64)
    numerator = np.power(data, Q + 1)
    denominator = np.power(data, Q)
    kernel = np.full(size, 1.0)
    result = filter2d(numerator, kernel) / filter2d(denominator, kernel)
    return array_to_img(result, img.mode)


def stat_filter2d(input_img, size, perc):
    """Apply a statistical filter to a 2-d image.

    max filter: perc=100
    min filter: perc=0
    median filter: perc=50
    """
    M, N = input_img.shape  # M is height, N is width
    m, n = size  # m is height, n is width
    a, b = m / 2, n / 2  # size of neighborhood

    def get_percentile(x, y):
        # z = np.zeros(n * m)  # pad with zeros
        z = []
        # fill in available neighborhood
        for i in xrange(x - a, x + a + 1):
            for j in xrange(y - b, y + b + 1):
                if i >= 0 and i < M and j >= 0 and j < N:
                    z.append(input_img[i, j])
        return percentile(z, perc)

    xx, yy = np.meshgrid(xrange(M), xrange(N), indexing='ij')
    vf = np.vectorize(get_percentile)
    return vf(xx, yy)


def percentile(arr, p):
    idx = p / 100.0 * (len(arr) - 1)
    sorted_arr = sorted(arr)
    below, above = int(floor(idx)), int(ceil(idx))
    return (sorted_arr[below] + sorted_arr[above]) / 2.0


def median_filter(img, size):
    """Apply a median filter to a 2-d image."""
    data = img_to_array(img)
    result = stat_filter2d(data, size, 50)
    return array_to_img(result, img.mode)


def max_filter(img, size):
    """Apply a max filter to a 2-d image."""
    data = img_to_array(img)
    result = stat_filter2d(data, size, 100)
    return array_to_img(result, img.mode)


def min_filter(img, size):
    """Apply a min filter to a 2-d image."""
    data = img_to_array(img)
    result = stat_filter2d(data, size, 0)
    return array_to_img(result, img.mode)


def geometric_mean(input_img, size):
    """Apply geometric mean filter to a 2-d image."""
    data = img_to_array(input_img, dtype=np.float64)
    M, N = data.shape  # M is height, N is width
    m, n = size  # m is height, n is width
    a, b = m / 2, n / 2

    def get_gmean(x, y):
        z = np.full(n * m, data[x, y])  # pad with border duplicates
        # fill in available neighborhood
        for i in xrange(x - a, x + a + 1):
            for j in xrange(y - b, y + b + 1):
                if i >= 0 and i < M and j >= 0 and j < N:
                    z[(i - x + a) * n + j - y + b] = data[i, j]
        # calculate power first to avoid overflow
        return np.prod(np.power(z, 1.0 / (m * n)))

    # apply to each pixel
    xx, yy = np.meshgrid(xrange(M), xrange(N), indexing='ij')
    vf = np.vectorize(get_gmean)
    return array_to_img(vf(xx, yy), input_img.mode)
