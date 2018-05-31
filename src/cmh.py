#!/usr/bin/env python
import logging
import logging.config
import sys

import defopt
import pandas as pd
import yaml
from dhalo import DHaloReader
from util import pmap

logging.config.dictConfig(yaml.load(open("./logging.yaml", "r")))
logger = logging.getLogger("main")


def main(filename, ids, nfw_f=0.02):
    """Compute CMH of a halo.

    :param str filename: HDF5 or cache file name.
    :param list[int] ids: list of nodeIndex values
    :param float nfw_f: NFW f parameter
    """
    reader = DHaloReader(filename)
    logger.debug("Initialised reader for %s file", filename)

    pd.concat(
        pmap(lambda i: reader.collapsed_mass_history(i, nfw_f), ids)
    ).pivot_table(
        index="nodeIndex",
        values="particleNumber",
        columns="snapshotNumber",
        fill_value=0,
    ).to_csv(
        sys.stdout, index=True, index_label="nodeIndex"
    )


if __name__ == "__main__":
    defopt.run(main)
