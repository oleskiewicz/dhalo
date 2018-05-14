#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def normalise(data, which):
    return data.apply(lambda x: x / x[which], 1)


if __name__ == '__main__':
    d = pd.read_csv(sys.argv[1], sep="\t")
    d = d.drop('nodeIndex', axis=1)
    # d = normalise(d.drop('nodeIndex', axis=1), -1)

    fig, ax = plt.subplots(1)

    for i, r in d.iterrows():
        ax.plot(map(int, r.index), np.log10(list(r)), c='gray', lw=1, ls='--')
    ax.plot(d.mean().index, np.log10(list(d.mean())), lw=3)

    ax.set_xlabel(r"$\texttt{snapshotNumber}$")
    ax.set_ylabel(r"$\log_{10}(\texttt{particleNumber})$")

    try:
        plotfile = sys.argv[2]
        plt.savefig(plotfile)
    except:
        plt.show()
