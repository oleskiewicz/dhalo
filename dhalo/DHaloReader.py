"""DHalo Reader module.
"""
#!/usr/bin/env python
import logging
import numpy as np
import h5py

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

        if self.filename.endswith(".npy"):
            data = np.load(open(self.filename, 'r'))

        elif self.filename.endswith(".hdf5"):
            with h5py.File(self.filename, 'r') as data_file:

                data = np.array(
                    zip(*[data_file['/haloTrees/%s' % column].values
                          for column in self.columns]),
                    dtype=[(column, 'int64')
                           for column in self.columns])

                with open("cache.npy", 'w') as cache_file:
                    np.save(cache_file, data)

        else:
            raise TypeError("Unknown filetype %s" % self.filename)

        return data

    def get_halo(self, index):
        """Returns halo (row of data) given a ``nodeIndex``

        :param int index: ``nodeIndex`` queried
        :return numpy.ndarray: row of argument ``d`` of the given ``nodeIndex``
        """
        try:
            halo = self.data[self.data['nodeIndex'] == index][0]
        except IndexError:
            raise IndexError("Halo of id %d not found" % index)
        return halo

    def halo_progenitors(self, halo):
        """Finds progenitors of halo.

        The following search is employed:

        - find all haloes of which ``h`` is a **host of a descendant**
        - find hosts of **these haloes**
        - keep unique ones
        """
        return np.array([
            self.get_halo(i) for i in np.unique([
                self.halo_host(progenitor)['nodeIndex']
                for progenitor in self.data[self.data['descendantHost'] == halo['nodeIndex']]
            ])
        ])

    def halo_host(self, halo):
        """Finds host of halo.

        Recursively continues until hits the main halo, in case of multiply embedded
        subhaloes.
        """
        return halo \
            if halo['nodeIndex'] == halo['hostIndex'] \
            else self.halo_host(self.data[self.data['nodeIndex'] == halo['hostIndex']][0])

    def halo_mass(self, halo):
        """Finds mass of central halo and all subhaloes.
        """
        return np.sum(self.data[self.data['hostIndex'] == halo['nodeIndex']]['particleNumber'])


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

        :param int i: ``nodeIndex`` of the starting halo
        :param numpy.ndarray data: dataset provided by :mod:`src.read` module
        :return List[int, List[]]: merger tree in a deeply mebedded format, rooted at
            the starting halo
        """

        halo = self.get_halo(index)
        if halo['hostIndex'] != halo['nodeIndex']:
            raise ValueError("Not a host halo!")

        progenitors = np.unique([
            p for p in self.data[self.data['descendantHost'] == halo['nodeIndex']]['hostIndex']
        ])

        logging.debug(
            "Reached halo %d with %d progenitor(s)" %
            (halo['nodeIndex'], len(progenitors)))

        return [
            halo['nodeIndex'], [] if len(progenitors) == 0 else
            [self.tree_build(p) for p in progenitors]
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

    def collapsed_mass_history(self, index, nfw_f):#tree, data, m0, nfw_f):
        """Calculates mass assembly history from a given merger tree.

        :param List[int, List[]] tree: merger tree, generated by :func:`tree`
        :param numpy.ndarray data: dataset provided by :mod:`src.read` module
        :param int m0: mass of the root halo
        :param float nfw_f: NFW :math:`f` parameter
        :return numpy.ndarray: MAH with rows formatted like ``[nodeIndex,
            snapshotNumber, sum(particleNumber)]``
        """

        cmh = []
        tree = self.tree_build(index)
        progenitors = np.array([self.get_halo(p) for p in self.tree_flatten(tree)])
        root = self.get_halo(tree[0])
        m0 = self.halo_mass(root)

        for snap in np.unique(progenitors['snapshotNumber']):
            sum_m = 0
            for h in progenitors[progenitors['snapshotNumber'] == snap]:
                m = self.halo_mass(h)
                if m > nfw_f * m0:
                    sum_m += m
            cmh.append([root['nodeIndex'], snap, sum_m])
        return np.array(cmh)
