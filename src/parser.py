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
    from bs4 import BeautifulSoup, Comment
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

        comments = soup.find_all(text=lambda text:isinstance(text, Comment))

        # - team offense infos
        # batting
        home_table = ''.join(home_team.split(' ')) + 'batting'

        comment = comments[[i
                            for i, com in enumerate(comments)
                            if home_table in com][0]]
        home_batting = BeautifulSoup(comment, 'html.parser')

        away_table = ''.join(away_team.split(' ')) + 'batting'

        comment = comments[[i
                            for i, com in enumerate(comments)
                            if away_table in com][0]]
        away_batting = BeautifulSoup(comment, 'html.parser')

        # gather total stats and ignore the details column
        home_stats = [(stat.attrs['data-stat'],
                       float(stat.contents[0]))
                      for stat in (home_batting.find(id=home_table)
                                               .find('tfoot')
                                               .find_all('td'))
                      if stat.attrs['data-stat'] != 'details']

        away_stats = [(stat.attrs['data-stat'],
                       float(stat.contents[0]))
                      for stat in (away_batting.find(id=away_table)
                                               .find('tfoot')
                                               .find_all('td'))
                      if stat.attrs['data-stat'] != 'details']

        # - starter infos (ERA, avg IP, WHIP)
        # pitching

        home_table = ''.join(home_team.split(' ')) + 'pitching'

        comment = comments[[i
                            for i, com in enumerate(comments)
                            if home_table in com][0]]
        home_pitching = BeautifulSoup(comment, 'html.parser')

        away_table = ''.join(away_team.split(' ')) + 'pitching'

        comment = comments[[i
                            for i, com in enumerate(comments)
                            if away_table in com][0]]
        away_pitching = BeautifulSoup(comment, 'html.parser')

        # gather total stats and ignore the inherited runners/score columns
        home_stats_pitching = [(stat.attrs['data-stat'],
                                float(stat.contents[0]))
                               for stat in (home_pitching.find(id=home_table)
                                                         .find('tbody')
                                                         .find('tr')
                                                         .find_all('td'))
                               if stat.attrs['data-stat'] not in ['inherited_runners',
                                                                  'inherited_score']]

        away_stats_pitching = [(stat.attrs['data-stat'],
                                float(stat.contents[0]))
                               for stat in (away_pitching.find(id=away_table)
                                                         .find('tbody')
                                                         .find('tr')
                                                         .find_all('td'))
                               if stat.attrs['data-stat'] not in ['inherited_runners',
                                                                  'inherited_score']]

        # bullpen ERA, fielding %, errors/9 IP, unearned runs/9 IP, stolen base %
        # pitching

        # gather total stats and ignore the inherited runners/score columns
        home_stats_team_pitching = [(stat.attrs['data-stat'],
                                float(stat.contents[0]))
                               for stat in (home_pitching.find(id=home_table)
                                                         .find('tfoot')
                                                         .find_all('td'))
                               if stat.attrs['data-stat'] not in ['inherited_runners',
                                                                  'inherited_score']]

        away_stats_team_pitching = [(stat.attrs['data-stat'],
                                float(stat.contents[0]))
                               for stat in (away_pitching.find(id=away_table)
                                                         .find('tfoot')
                                                         .find_all('td'))
                               if stat.attrs['data-stat'] not in ['inherited_runners',
                                                                  'inherited_score']]

        # - wind, sun, rain, humidity, weather in general

        comment = comments[[i
                            for i, com in enumerate(comments)
                            if 'div_1954100963' in com][0]]
        weather_data = BeautifulSoup(comment, 'html.parser')

        for info_div in weather_data.find_all('div'):
            if any((x.string or '').startswith('Start Time Weather') for x in info_div.children):
                weather = info_div.contents[1].split(': ')[1]

        # errors

        linescore = soup.find('table',
                              class_='linescore nohover stats_table no_freeze').find('tbody')

        away_line = linescore.find('tr')
        away_errors = int(away_line.find_all('td')[-1].contents[0])

        home_line = away_line.find_next_sibling('tr')
        home_errors = int(away_line.find_all('td')[-1].contents[0])

        # - park stats (sizes down RF, CF, LF, foul territory %?) are missing

        infos = [home_team,
                 away_team,
                 venue,
                 start_time,
                 date_played,
                 away_errors,
                 home_errors,
                 weather,
                 *[x[1] for x in away_stats],
                 *[x[1] for x in home_stats],
                 *[x[1] for x in away_stats_pitching],
                 *[x[1] for x in home_stats_pitching],
                 *[x[1] for x in away_stats_team_pitching],
                 *[x[1] for x in home_stats_team_pitching],
                 ]
        infos_q.put(infos)

        with links_count.get_lock():
            links_count.value += 1
