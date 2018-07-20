"""DHalo Reader module.
"""
#!/usr/bin/env python3
import os
import yaml
import logging
import numpy as np
import pandas as pd
import h5py

logging.basicConfig(level=logging.DEBUG)


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
            logging.debug("Loading pickle file %s", self.filename)
            data = pd.read_pickle(self.filename)

        elif self.filename.endswith(".hdf5"):
            logging.debug("Loading HDF5 file %s", self.filename)
            with h5py.File(self.filename, "r") as data_file:

                data = pd.DataFrame(
                    {
                        column: data_file["/haloTrees/%s" % column].value
                        for column in self.columns
                    }
                ).set_index("nodeIndex")

                # with open("./data/cache.pkl", "w") as pickle_file:
                #     data.to_pickle(pickle_file)

        else:
            raise TypeError("Unknown filetype %s" % self.filename)

        return data

    def get_halo(self, index):
        """Returns halo (row of data) given a ``nodeIndex``

        :param int index: ``nodeIndex`` queried
        :return numpy.ndarray: row of argument ``d`` of the given ``nodeIndex``
        """
        try:
            halo = self.data.loc[index]
        except KeyError:
            raise IndexError(
                "Halo id %d not found in %s" % (index, self.filename)
            )
        return halo

    def halo_progenitor_ids(self, index):
        """Finds indices of all progenitors of a halo, recursively.

        The following search is employed:

        - find all haloes of which ``h`` is a **host of a descendant**
        - find hosts of **these haloes**
        - keep unique ones
        """
        _progenitors = []

        def rec(i):
            _progenitor_ids = self.data[self.data["descendantHost"] == i][
                "hostIndex"
            ].unique()
            logging.debug(
                "Progenitors recursion: %d > %d (%d progenitors)",
                index,
                i,
                len(_progenitor_ids),
            )
            if len(_progenitor_ids) == 0:
                return
            for _progenitor_id in _progenitor_ids:
                # if _progenitor_id not in _progenitors: # TODO: this only eliminates fly-byes
                _progenitors.append(_progenitor_id)
                rec(_progenitor_id)

        rec(index)

        logging.info(
            "%d progenitors found for halo %d", len(_progenitors), index
        )
        return _progenitors

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

    def collapsed_mass_history(self, index, nfw_f):
        """Calculates mass assembly history for a given halo.

        Tree-based approach has been abandoned for performace reasons.

        :param int index: nodeIndex
        :param float nfw_f: NFW :math:`f` parameter
        :return numpy.ndarray: CMH with rows formatted like ``[nodeIndex,
            snapshotNumber, sum(particleNumber)]``
        """

        logging.debug("Looking for halo %d", index)
        halo = self.get_halo(index)
        if halo["hostIndex"] != halo.name:
            raise ValueError("Not a host halo!")
        m_0 = self.halo_mass(index)

        progenitors = pd.concat(
            [
                self.data.loc[index],
                self.data.loc[self.halo_progenitor_ids(index)],
            ]
        )
        logging.debug(
            "Built progenitor sub-table for halo %d of mass %d with %d members",
            index,
            m_0,
            progenitors.size,
        )

        progenitors = progenitors[progenitors["particleNumber"] > nfw_f * m_0]
        cmh = progenitors.groupby("snapshotNumber", as_index=False)[
            "particleNumber"
        ].sum()
        cmh["nodeIndex"] = index
        logging.info(
            "Aggregated masses of %d valid progenitors of halo %d",
            progenitors.size,
            index,
        )

        return cmh
