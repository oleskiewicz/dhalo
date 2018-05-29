#!/usr/bin/env python
import defopt
import yaml
from dhalo import DHaloReader


def main(filename, index, nfw_f=0.02):
    """Compute CMH of a halo.

    :param str filename: HDF5 or cache file name.
    :param int index: nodeIndex
    :param float nfw_f: NFW f parameter
    """
    reader = DHaloReader(filename)
    print(reader.collapsed_mass_history(index, nfw_f))


if __name__ == "__main__":
    defopt.run(main)
