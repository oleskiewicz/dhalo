#!/usr/bin/env python
import sys
import pandas as pd


def cast(data):
    """Un-melts (casts) the DataFrame from long format to a wide one

    In essence, we want to go from

    =============== =============== ==============
    nodeIndex       snapshotNumber  particleNumber
    =============== =============== ==============
    30048700000139  11              0
    30048700000139  12              0
    30048700000139  13              0
    30048700000139  14              324
    30048700000139  15              653
    30048700000139  16              849
    30048700000139  17              1204
    30048700000139  ...             ...
    30050100000241  10              0
    30050100000241  11              0
    30050100000241  12              0
    30050100000241  13              0
    30050100000241  14              0
    30050100000241  15              132
    30050100000241  16              661
    30050100000241  17              945
    30050100000241  ...             ...
    ...
    =============== =============== ==============

    to

    =============== ==== ==== ==== ==== ==== ==== ==== ==== ===
    id              10   11   12   13   14   15   16   17   ...
    =============== ==== ==== ==== ==== ==== ==== ==== ==== ===
    30048700000139  NA   0    0    0    324  653  849  1204 ...
    30050100000241  0    0    0    0    0    132  661  945  ...
    ...
    =============== ==== ==== ==== ==== ==== ==== ==== ==== ===

    as described in https://cran.r-project.org/web/packages/reshape2/reshape2.pdf

    Arguments:
        data (pandas.DataFrame): input MAH DataFrame in a long format, read from a
            TSV written by :mod:`src.tree`
    Returns:
        pandas.DataFrame: output MAH DataFrame in a wide format
    """
    return data.pivot_table(\
     values='particleNumber',\
     index='nodeIndex',
     columns='snapshotNumber')


if __name__ == '__main__':
    tsv = sys.argv[1]
    long = pd.read_csv(tsv, sep="\t")
    wide = cast(long)
    wide.to_csv(tsv, sep="\t")
