#!/usr/bin/env python3
import fcntl
import logging
import sys

import numpy as np

from . import halo, read


def build(id, data):
    """Generates merger tree from data

    Recursively generates a merger tree of the format::

        [1, [[2, []], [3, [[4, []], [5, []]]], [6, []]]]

    equivalent to::

        1
            2
            3
                4
                5
            6

    Arguments:
        id (int): ``nodeIndex`` of the starting halo
        data (numpy.ndarray): dataset provided by :mod:`src.read` module
    Returns:
        list: merger tree in a deeply mebedded format, rooted at the starting
            halo
    """
    if not halo.is_host(id, d):
        raise ValueError("Not a host halo!")

    h = halo.get(id, data)
    progenitors = halo.progenitors(h, data)
    logging.debug(
        "Reached halo %d with %d progenitor(s)"
        % (h["nodeIndex"], len(progenitors))
    )
    return [
        h["nodeIndex"],
        []
        if len(progenitors) == 0
        else [build(progenitor, data) for progenitor in progenitors],
    ]


def flatten(tree):
    """Finds all ``nodeIndex`` values belonging to a given merger tree

    Arguments:
        tree (list): merger tree generated by :func:`build`
    Returns:
        generator: to be fed as an argument to the ``list()`` function
    **References:**
        https://stackoverflow.com/a/2158532
    """
    for node in tree:
        try:
            for subnode in flatten(node):
                yield subnode
        except:
            yield node


def mah(tree, progs, data, m0, nfw_f):
    """Calculates mass assembly history from a given merger tree

    Arguments:
        tree (list): merger tree, generated by :func:`tree`
        progs (numpy.ndarray): all prigenitors of the root halo in a merger
            tree (effectively a flattened tree), calculated by :func:`flatten`,
            a subset of ``data``
        data (numpy.ndarray): dataset provided by :mod:`src.read` module
        m0 (int): mass of the root halo
        nfw_f (float): NFW :math:`f` parameter
    Returns:
        numpy.ndarray: MAH with rows formatted like ``[nodeIndex,
            snapshotNumber, sum(particleNumber)]``
    """
    mah = []
    root = halo.get(tree[0], progs)

    for snap in np.unique(progs["snapshotNumber"]):
        sum_m = 0
        for h in progs[progs["snapshotNumber"] == snap]:
            m = halo.mass(h, data)
            if m > nfw_f * m0:
                sum_m += m
        mah.append([root["nodeIndex"], snap, sum_m])
    return np.array(mah)


if __name__ == "__main__":
    # # array submission
    # with open("./output/ids.txt") as file_ids:
    #   for i, line in enumerate(file_ids):
    #       if i == int(sys.argv[1])-1:
    #           root = int(line)
    # single-job submission
    file_numpy = sys.argv[1]
    root = int(sys.argv[2])
    file_csv = sys.argv[3]

    d = read.retrieve(file_numpy)
    h = halo.get(root, d)

    nfw_f = 0.01
    m0 = halo.mass(h, d)
    logging.info(
        "Found halo %d of mass %d at snapshot %d"
        % (root, m0, h["snapshotNumber"])
    )

    t = build(h, d)
    p = np.array([halo.get(id, d) for id in list(flatten(t))])
    m = mah(t, p, d, m0, nfw_f)
    logging.info(
        "Built a tree rooted at halo %d with %d children" % (root, p.shape[0])
    )

    with open(file_csv, "a") as file_csv:
        fcntl.flock(file_csv, fcntl.LOCK_EX)
        logging.info("Locked %s" % (file_csv.name))
        for row in m:
            file_csv.write("%d,%02d,%d\n" % (row[0], row[1], row[2]))
        fcntl.flock(file_csv, fcntl.LOCK_UN)
        logging.info(
            "Appended MAH of %d to %s, unlocking file" % (root, file_csv.name)
        )

    # with open("./test.dot", 'w') as file_dot:
    #   file_dot.write("digraph merger_tree { rankdir=BT;\n")
    #   dot.tree(file_dot, t, d, m0, nfw_f)
    #   file_dot.write("\tsubgraph snapshots {\n")
    #   dot.mah(file_dot, m, p)
    #   file_dot.write("\t}\n")
    #   file_dot.write("}\n")
    #   logging.info("Wrote Dot graph to %s"%(file_dot.name))
