#!/usr/bin/env python3
import logging
import sys

import defopt
import pandas as pd

from dhalo import DHaloReader
from src.util import pmap

logging.basicConfig(level=logging.DEBUG)


def main(data_file, ids_file, nfw_f=0.02):
    """Compute CMH of a halo.

    :param str data_file: HDF5 or cache file name.
    :param str ids_file: text file with nodeIndex values
    :param float nfw_f: NFW f parameter
    """

    ids = pd.read_table(ids_file).values[:, 0]
    logging.info("Loaded %d ids from %s", len(ids), ids_file)

    reader = DHaloReader(data_file)
    logging.info("Initialised reader for %s file", data_file)

    pd.concat(
        pmap(lambda i: reader.collapsed_mass_history(i, nfw_f), ids, 8)
    ).pivot_table(
        index="nodeIndex",
        values="particleNumber",
        columns="snapshotNumber",
        fill_value=0,
    ).to_csv(
        sys.stdout, index=True, index_label="nodeIndex"
    )

    logging.info("Pivoted CMHs for %d haloes, exiting.", len(ids))


if __name__ == "__main__":
    defopt.run(main)
