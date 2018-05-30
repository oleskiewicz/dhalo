#!/usr/bin/env python
import sys

import halo
import numpy as np
import read


def process(data, query):
    """Process query on a data set

    Example:

        This query retuns halo IDs for top 100 most massive haloes at snapshot 30:

        .. code-block:: python

            q = {
                'filter': {
                    'by': 'snapshotNumber',
                    'value': 63,
                },
                'limit': {
                    'n': 10,
                },
                'select': {
                    'by': 'nodeIndex',
                },
            }

    Arguments:
        data (numpy.ndarray): dataset provided by :mod:`src.read` module
        query (dict): query to be processed (see `Example`)
    """
    # TODO: h['hostIndex'] -> halo.host(h, data)['nodeIndex'] gives TypeError
    return np.unique(
        [
            h["hostIndex"]
            for h in data[
                data[query["filter"]["by"]] == query["filter"]["value"]
            ]
        ]
    )


if __name__ == "__main__":
    d = read.data(sys.artgv[2])

    q = {
        "filter": {"by": "snapshotNumber", "value": 63},
        "limit": {"n": -1},
        "select": {"by": "nodeIndex"},
    }

    ids = process(d, q)

    with open(sys.argv[1], "w") as f:
        for i in ids:
            f.write("%d\n" % i)
