#! /usr/bin/env python3

import time


def queue_filler(q, queue_size, links):
    for link in links:
        q.put(link)
        if q.qsize() >= queue_size:
            time.sleep(1)
    print('exiting queue filler')
    return


def write_infos(q, links_count):
    import queue

    written = 0
    start_time = time.time()

    # one folder up, into the 'data' folder
    current_dir = path.dirname(path.abspath(__file__))
    file_loc = path.join(current_dir, '..', 'data', 'player_infos.csv')

    colnames = [  # column names for the data here
                ]

    with open(file_loc, 'w') as f:
        f.write(','.join(colnames) + '\n')

        # give the queue some time to fill up
        time.sleep(10)
        while written < links_count.value:
            try:
                infos = q.get(timeout=5)
            except queue.Empty:
                print('    Infos queue empty!    ')
                time.sleep(1)
                continue

            f.write(','.join(infos) + '\n')
            written += 1
            if written % 1000 == 0:
                print('\rParsed {}/{} in {}'.format(written,
                                                    links_count.value,
                                                    time.time() - start_time))
        print('exiting write_infos')
    return


if __name__ == '__main__':
    from os import path
    import multiprocessing
    from parser import get_player_infos

    queue_size = 1000

    # one folder up, into the 'data' folder
    current_dir = path.dirname(path.abspath(__file__))
    file_loc = path.join(current_dir, '..', 'data', 'player_links.txt')

    with open(file_loc, 'r') as f:
        links = set(f.read().split('\n'))

    links_count = multiprocessing.Value('i', 0)
    q = multiprocessing.Queue()
    infos_q = multiprocessing.Queue()

    # initialize queue filler
    p1 = multiprocessing.Process(target=queue_filler,
                                 args=(q, queue_size, links))
    p1.start()

    procs = {}

    for p in range(0, 10):
        procs[p] = multiprocessing.Process(target=get_player_infos,
                                           args=(q,
                                                 infos_q,
                                                 links_count))
        procs[p].start()

    # initialize writer
    p2 = multiprocessing.Process(target=write_infos,
                                 args=(infos_q, links_count))
    p2.start()

    p1.join()

    for p in range(0, 10):
        procs[p].join()

    p2.join()
