#!/usr/bin/env python3
import logging
import sys

import defopt

from dhalo import DHaloReader

logging.basicConfig(level=logging.DEBUG)


def main(filename, snapshot):
    """Query IDs of haloes.

    :param str filename: HDF5 or cache file name.
    :param int snapshot: Snapshot number
    """

    reader = DHaloReader(filename)
    logging.debug("Initialised reader for %s file", filename)

    data = reader.data[reader.data["snapshotNumber"] == snapshot]

    ids = data.loc[
        [reader.halo_host(i).name for i in data.index]
    ].index.unique()

    for i in ids:
        sys.stdout.write("%d\n" % i)


if __name__ == "__main__":
    defopt.run(main)
