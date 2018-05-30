"""DHalo Reader module.
"""
#!/usr/bin/env python
import yaml
import logging, logging.config
import numpy as np
import pandas as pd
import h5py

logging.config.dictConfig(yaml.load(open("./logging.yaml", "r")))
logger = logging.getLogger("DHaloReader")


class DHaloReader(object):
    """DHalo Reader class.
    """

    def __init__(self, filename):
        self.filename = filename
        self.columns = [
            "nodeIndex",
            "descendantIndex",
            "snapshotNumber",
            "particleNumber",
            "hostIndex",
            "descendantHost",
            "isMainProgenitor",
        ]
        self.data = self.read()

    def read(self):
        """Reads DHalo data into memory

        Output data format:

        ===========  ==================
         Column ID    Column Name
        ===========  ==================
                 0    nodeIndex
                 1    descendantIndex
                 2    snapshotNumber
                 3    particleNumber
                 4    hostIndex
                 5    descendantHost
                 6    isMainProgenitor
        ===========  ==================

        nodeIndex:
            index of each halo or subhalo, unique across the entire catalogue
        descendantIndex:
            index of a descendanta halo (if multiple haloes have the same
            descendatant index, they all are the progenitors)
        snapshotNumber:
            snapshot at which halo was identified
        particleNumber:
            number of particles in a halo; might differ from masses identified
            by other methods
        hostIndex:
            index of a host halo; for subhaloes, this points to a parent halo;
            for main haloes, this points to themselves
        descendantHost:
            index of a host halo of descendant of a halo (or subhalo); this
            field eliminates "multiple descendance" problem, always creating a
            merger history which works for main progenitors only
        isMainProgenitor:
            1 if it is
        """

        if self.filename.endswith(".pkl"):
            data = pd.read_pickle(self.filename)

        elif self.filename.endswith(".hdf5"):
            with h5py.File(self.filename, "r") as data_file:

                data = pd.DataFrame(
                    zip(
                        *[
                            data_file["/haloTrees/%s" % column].values
                            for column in self.columns
                        ]
                    ),
                    dtype=[(column, "int64") for column in self.columns],
                )

                with open("cache.pkl", "w") as pickle_file:
                    data.to_pickle(pickle_file)

        else:
            raise TypeError("Unknown filetype %s" % self.filename)

        return data

    def get_halo(self, index):
        """Returns halo (row of data) given a ``nodeIndex``

        :param int index: ``nodeIndex`` queried
        :return numpy.ndarray: row of argument ``d`` of the given ``nodeIndex``
        """
        try:
            # halo = self.data.loc[index]
            halo = self.data.loc[index]
        except KeyError:
            raise IndexError(
                "Halo id %d not found in %s" % (index, self.filename)
            )
        return halo

    def halo_progenitors(self, index):
        """Finds progenitors of halo.

        The following search is employed:

        - find all haloes of which ``h`` is a **host of a descendant**
        - find hosts of **these haloes**
        - keep unique ones
        """
        return self.data.loc[
            np.unique(
                self.data[self.data["descendantHost"] == index]["hostIndex"]
            )
        ]

    def halo_host(self, index):
        """Finds host of halo.

        Recursively continues until hits the main halo, in case of multiply embedded
        subhaloes.
        """
        halo = self.get_halo(index)
        return (
            halo
            if halo.name == halo["hostIndex"]
            else self.halo_host(self.get_halo(halo["hostIndex"]).name)
        )

    def halo_mass(self, index):
        """Finds mass of central halo and all subhaloes.
        """
        return self.data[self.data["hostIndex"] == index][
            "particleNumber"
        ].sum()

    def tree_build(self, index):
        """Generates merger tree from tabular data.

        Recursively generates a merger tree of the format::

            [1, [[2, []], [3, [[4, []], [5, []]]], [6, []]]]

        equivalent to::

            1
                2
                3
                    4
                    5
                6

        .. Warning::

            Deprecated - new data format is Pandas, this is **not** going to
            work!

        :param int i: ``nodeIndex`` of the starting halo
        :param numpy.ndarray data: dataset provided by :mod:`src.read` module
        :return List[int, List[]]: merger tree in a deeply mebedded format, rooted at
            the starting halo
        """

        halo = self.get_halo(index)
        if halo["hostIndex"] != halo["nodeIndex"]:
            raise ValueError("Not a host halo!")

        progenitors = np.unique(
            [
                p
                for p in self.data[
                    self.data["descendantHost"] == halo["nodeIndex"]
                ]["hostIndex"]
            ]
        )

        logger.debug(
            "Reached halo %d with %d progenitor(s)",
            halo["nodeIndex"],
            len(progenitors),
        )

        return [
            halo["nodeIndex"],
            []
            if progenitors.size == 0
            else [self.tree_build(p) for p in progenitors],
        ]

    def tree_flatten(self, tree):
        """Finds all ``nodeIndex`` values belonging to a given merger tree

        **Reference:** https://stackoverflow.com/a/2158532

        :param List[int, List[]] tree: merger tree generated by :func:`build`
        :return generator: flattened N-D list
        """

        for node in tree:
            try:
                for subnode in self.tree_flatten(node):
                    yield subnode
            except:
                yield node

    def collapsed_mass_history(self, index, nfw_f):  # tree, data, m0, nfw_f):
        """Calculates mass assembly history for a given halo.

        Tree-based approach has been abandoned for performace reasons.

        :param int index: nodeIndex
        :param float nfw_f: NFW :math:`f` parameter
        :return numpy.ndarray: CMH with rows formatted like ``[nodeIndex,
            snapshotNumber, sum(particleNumber)]``
        """

        logger.debug("Starting with halo %d", index)

        cmh = []
        halo = self.get_halo(index)
        if halo["hostIndex"] != halo.name:
            raise ValueError("Not a host halo!")
        m_0 = self.halo_mass(index)
        print("Found halo %d of mass %d", index, m_0)

        def children(i):
            list_of_children = []

            def rec(i):

                print(i)
                h = self.get_halo(i)
                child_ids = self.data[self.data["descendantHost"] == h.name][
                    "hostIndex"
                ]
                if child_ids.empty:
                    return
                for child_id in child_ids:
                    list_of_children.append(child_id)
                    rec(child_id)

            rec(i)
            return list_of_children

        print(children(index))

        # TODO: calculate CMH efficiently

        return np.array(cmh)
