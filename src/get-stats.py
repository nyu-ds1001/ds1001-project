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
    file_loc = path.join(current_dir, '..', 'data', 'game_infos.csv')

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
    from parser import get_player_infos, get_team_links

    teams = get_team_links('https://www.baseball-reference.com/teams/', )

    years = []

    for team in teams:
        years.append(get_team_years(team))

    games = multiprocessing.Queue()
    for year in years:
        get_team_games(year, games)

    links_count = multiprocessing.Value('i', 0)
    infos_q = multiprocessing.Queue()

    procs = {}

    for p in range(0, 10):
        procs[p] = multiprocessing.Process(target=parse_team_games,
                                           args=(games,
                                                 infos_q,
                                                 links_count))
        procs[p].start()

    # initialize writer
    p2 = multiprocessing.Process(target=write_infos,
                                 args=(infos_q, links_count))
    p2.start()

    for p in range(0, 10):
        procs[p].join()

    p2.join()
