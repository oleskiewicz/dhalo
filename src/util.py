#!/usr/bin/env python3
import multiprocessing as mp


def pmap(f, xs, nprocs=mp.cpu_count()):
    """Parallel map.

    As seen in: <https://stackoverflow.com/a/16071616>.
    """

    def __f(f, q_in, q_out):
        while True:
            i, x = q_in.get()
            if i is None:
                break
            q_out.put((i, f(x)))

    q_in = mp.Queue(1)
    q_out = mp.Queue()

    proc = [
        mp.Process(target=__f, args=(f, q_in, q_out)) for _ in range(nprocs)
    ]

    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(xs)]

    for _ in range(nprocs):
        q_in.put((None, None))

    res = [q_out.get() for _ in range(len(sent))]

    for p in proc:
        p.join()

    return [x for i, x in res]
