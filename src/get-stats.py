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
    from os import path

    written = 0
    start_time = time.time()

    # one folder up, into the 'data' folder
    current_dir = path.dirname(path.abspath(__file__))
    file_loc = path.join(current_dir, '..', 'data', 'game_infos.csv')

    colnames = ['home_team',
                'away_team',
                'venue',
                'start_time',
                'date_played',
                'away_errors',
                'home_errors',
                'weather_info',
                'AB_home',
                'R_home',
                'H_home',
                'RBI_home',
                'BB_home',
                'SO_home',
                'PA_home',
                'BA_home',
                'OBP_home',
                'SLG_home',
                'OPS_home',
                'Pit_home',
                'Str_home',
                'WPA_home',
                'aLI_home',
                'WPA+_home',
                'WPA-_home',
                'RE24_home',
                'PO_home',
                'A_home',
                'AB_away',
                'R_away',
                'H_away',
                'RBI_away',
                'BB_away',
                'SO_away',
                'PA_away',
                'BA_away',
                'OBP_away',
                'SLG_away',
                'OPS_away',
                'Pit_away',
                'Str_away',
                'WPA_away',
                'aLI_away',
                'WPA+_away',
                'WPA-_away',
                'RE24_away',
                'PO_away',
                'A_away',
                'IP_player_away',
                'H_player_away',
                'R_player_away',
                'ER_player_away',
                'BB_player_away',
                'SO_player_away',
                'HR_player_away',
                'ERA_player_away',
                'BF_player_away',
                'Pit_player_away',
                'Str_player_away',
                'Ctct_player_away',
                'StS_player_away',
                'StL_player_away',
                'GB_player_away',
                'FB_player_away',
                'LD_player_away',
                'Unk_player_away',
                'GSc_player_away',
                'IR_player_away',
                'IS_player_away',
                'WPA_player_away',
                'aLI_player_away',
                'RE24_player_away',
                'IP_player_home',
                'H_player_home',
                'R_player_home',
                'ER_player_home',
                'BB_player_home',
                'SO_player_home',
                'HR_player_home',
                'ERA_player_home',
                'BF_player_home',
                'Pit_player_home',
                'Str_player_home',
                'Ctct_player_home',
                'StS_player_home',
                'StL_player_home',
                'GB_player_home',
                'FB_player_home',
                'LD_player_home',
                'Unk_player_home',
                'GSc_player_home',
                'IR_player_home',
                'IS_player_home',
                'WPA_player_home',
                'aLI_player_home',
                'RE24_player_home',
                'IP_team_away',
                'H_team_away',
                'R_team_away',
                'ER_team_away',
                'BB_team_away',
                'SO_team_away',
                'HR_team_away',
                'ERA_team_away',
                'BF_team_away',
                'Pit_team_away',
                'Str_team_away',
                'Ctct_team_away',
                'StS_team_away',
                'StL_team_away',
                'GB_team_away',
                'FB_team_away',
                'LD_team_away',
                'Unk_team_away',
                'GSc_team_away',
                'IR_team_away',
                'IS_team_away',
                'WPA_team_away',
                'aLI_team_away',
                'RE24_team_away',
                'IP_team_home',
                'H_team_home',
                'R_team_home',
                'ER_team_home',
                'BB_team_home',
                'SO_team_home',
                'HR_team_home',
                'ERA_team_home',
                'BF_team_home',
                'Pit_team_home',
                'Str_team_home',
                'Ctct_team_home',
                'StS_team_home',
                'StL_team_home',
                'GB_team_home',
                'FB_team_home',
                'LD_team_home',
                'Unk_team_home',
                'GSc_team_home',
                'IR_team_home',
                'IS_team_home',
                'WPA_team_home',
                'aLI_team_home',
                'RE24_team_home',
                ]

    with open(file_loc, 'w') as f:
        f.write(','.join(colnames) + '\n')

        # give the queue some time to fill up
        time.sleep(30)
        while written < 97200:
            try:
                infos = q.get(timeout=5)
            except queue.Empty:
                print('    Infos queue empty!    ')
                time.sleep(30)
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
    from parser_bbref import get_player_infos, get_team_links, get_team_years
    from parser_bbref import get_team_games, parse_team_games

    teams = get_team_links('https://www.baseball-reference.com/teams/', )

    years = []

    for team in teams:
        years.append(get_team_years(team))

    games = multiprocessing.Queue()
    for team in years:
        for year in team:
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
