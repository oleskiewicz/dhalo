#!/usr/bin/env python
import logging
import sys

import numpy as np


def get(h, d):
    """Returns halo (row of data) given a ``nodeIndex``

    :param int h: ``nodeIndex`` queried
    :param numpy.ndarray d: DHalo tree data, as provided by :mod:`src.read`
    :return numpy.ndarray: row of argument ``d`` of the given ``nodeIndex``
    """
    try:
        h = d[d["nodeIndex"] == h][0]
    except IndexError:
        raise IndexError("Halo of id %d not found" % h)
    return h


def progenitors(h, d):
    """Finds progenitors of ``h``

    The following search is employed:

    - find all haloes of which ``h`` is a **host of a descendant**
    - find hosts of **these haloes**
    - keep unique ones
    """
    return np.array(
        [
            get(i, d)
            for i in np.unique(
                [
                    host(prog, d)["nodeIndex"]
                    for prog in d[d["descendantHost"] == h["nodeIndex"]]
                ]
            )
        ]
    )


def host(h, d):
    """Finds host of ``h``

    Recursively continues until hits the main halo, in case of multiply embedded
    subhaloes.
    """
    return (
        h
        if h["nodeIndex"] == h["hostIndex"]
        else host(d[d["nodeIndex"] == h["hostIndex"]][0], d)
    )


def is_host(h, d):
    """Checks if halo is a main halo using :func:`host`
    """
    return h["nodeIndex"] == h["hostIndex"]


def descendant(h, d):
    """Finds descendant of ``h``
    """
    return d[d["nodeIndex"] == h["descendantIndex"]][0]


def descendant_host(h, d):
    """Finds host of a descendant of ``h``

    DHalo uses this value to keep track of the most massive part of subhaloes in
    case of splitting, preventing "multiply-progenitored" haloes.
    """
    return d[d["nodeIndex"] == h["descendantHost"]][0]


def subhaloes(h, d):
    """Finds halo indices for which ``h`` is a host
    """
    return d[d["hostIndex"] == h["nodeIndex"]]


def mass(h, d):
    """Finds mass of central halo and all subhaloes
    """
    return np.sum(d[d["hostIndex"] == h["nodeIndex"]]["particleNumber"])
