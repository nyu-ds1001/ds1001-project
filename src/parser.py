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
    import time

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

        infos_q.put(infos)
