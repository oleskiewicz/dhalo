#!/usr/bin/env python3
import multiprocessing as mp


def pmap(f, xs, nprocs=mp.cpu_count()):
    """Parallel map.

    As seen in: <https://stackoverflow.com/a/16071616>.
    """

    def fun(f, q_in, q_out):
        while True:
            i, x = q_in.get()
            if i is None:
                break
            q_out.put((i, f(x)))

    q_in = mp.Queue(1)
    q_out = mp.Queue()

    proc = [
        mp.Process(target=fun, args=(f, q_in, q_out)) for _ in xrange(nprocs)
    ]

    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(xs)]
    [q_in.put((None, None)) for _ in xrange(nprocs)]
    res = [q_out.get() for _ in xrange(len(sent))]

    [p.join() for p in proc]

    return [x for i, x in res]
