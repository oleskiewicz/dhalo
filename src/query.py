#!/usr/bin/env python
import logging
import logging.config
import os
import sys

import defopt
import pandas as pd
import yaml
from dhalo import DHaloReader

logging.config.dictConfig(
    yaml.load(
        open(
            os.path.join(os.path.dirname(__file__) + "/../", "./logging.yaml"),
            "r",
        )
    )
)
logger = logging.getLogger(__name__)


def main(filename, snapshot):
    """Query IDs of haloes.

    :param str filename: HDF5 or cache file name.
    :param int snapshot: Snapshot number
    """

    reader = DHaloReader(filename)
    logger.debug("Initialised reader for %s file", filename)

    data = reader.data[reader.data["snapshotNumber"] == snapshot]

    ids = data.loc[
        [reader.halo_host(i).name for i in data.index]
    ].index.unique()

    for i in ids:
        sys.stdout.write("%d\n" % i)


if __name__ == "__main__":
    defopt.run(main)
