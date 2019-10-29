#! /usr/bin/env python3


def get_player_infos(q, infos_q, links_count):
    raise NotImplementedError


def get_team_links(link):
    import requests
    from bs4 import BeautifulSoup

    links_q = []

    page = requests.get(link)
    if page.status_code != 200:
        print('Failed requesting page {}!'.format(link))
        page.raise_for_status()

    soup = BeautifulSoup(page.text, 'html.parser')

    section = soup.find('table', id='teams_active')

    results = set()
    for hyperlink in section.find_all('a'):
        full_link = 'http://www.baseballreference.com' + hyperlink.get('href')
        if full_link not in results:
            links_q.append(full_link)
            results.add(full_link)

    return links_q


def get_team_years(link):
    import requests
    from bs4 import BeautifulSoup

    years_q = []

    page = requests.get(link)
    if page.status_code != 200:
        print('Failed requesting page {}!'.format(link))
        page.raise_for_status()

    soup = BeautifulSoup(page.text, 'html.parser')

    section = soup.find('table', id='franchise_years')

    for hyperlink in section.find_all('a'):
        full_link = 'http://www.baseballreference.com' + hyperlink.get('href')
        years_q.append(full_link)

    return years_q
    

def get_team_games(link, games_q):
    import requests
    from bs4 import BeautifulSoup

    page = requests.get(link)
    if page.status_code != 200:
        print('Failed requesting page {}!'.format(link))
        page.raise_for_status()

    soup = BeautifulSoup(page.text, 'html.parser')

    section = soup.find('div', id='timeline_results')

    for hyperlink in section.find_all('a'):
        full_link = 'http://www.baseballreference.com' + hyperlink.get('href')
        games_q.put(full_link)


def parse_team_games(q, infos_q, links_count):
    import requests
    from bs4 import BeautifulSoup
    import queue
    import re
    import time

    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    while True:
        try:
            link = q.get(timeout=5)
        except queue.Empty:
            print('     Links queue empty!    ')
            break

        page = requests.get(link)
        if page.status_code != 200:
            print('Failed requesting page {}!'.format(link))
            page.raise_for_status()

        infos = []
        soup = BeautifulSoup(page.text, 'html.parser')

        # find all the info we need and add to infos list

        # - matchup info (what teams?)
        
        h1 = soup.find('h1', )
        teams = re.search(r'(.+?) at (.+?) Box Score', h1.string)
        away_team = teams.group(1)
        home_team = teams.group(2)

        # - time of game (time of day, day of week, year played, month played)

        div = soup.find('div', class_='scorebox_meta')

        for info_div in div.find_all('div'):
            if any((x.string or '').startswith('Venue') for x in info_div.children):
                venue = info_div.contents[1].split(': ')[1]
            elif any((x.string or '').startswith('Start Time') for x in info_div.children):
                start_time = info_div.contents.split('Start Time: ')[1]
            elif any(any((x.string or '').startswith(y) for y in weekdays) for x in info_div.children):
                date_played = info_div.contents[0].split('day, ')[1]

        # - wind, sun, rain, humidity, weather in general
        # div_1954100963 - somehow is a comment but not when i load the html on browser
        # - park stats (sizes down RF, CF, LF, foul territory %?)
        # - team infos (ERA, WHIP, OPS, bullpen ERA, fielding %, errors/9 IP, unearned runs/9 IP, stolen base %)
        # - starter infos (ERA, avg IP, WHIP)

        infos_q.put(infos)

        with links_count.get_lock():
            links_count.value += 1
