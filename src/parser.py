#! /usr/bin/env python3


def get_player_infos(q, infos_q, links_count):
    raise NotImplementedError


def get_team_links(link, links_q):
    import requests
    from bs4 import BeautifulSoup

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
            links_q.put(full_link)
            results.add(full_link)


def get_team_years(link, years_q):
    import requests
    from bs4 import BeautifulSoup

    page = requests.get(link)
    if page.status_code != 200:
        print('Failed requesting page {}!'.format(link))
        page.raise_for_status()

    soup = BeautifulSoup(page.text, 'html.parser')

    section = soup.find('table', id='franchise_years')

    for hyperlink in section.find_all('a'):
        full_link = 'http://www.baseballreference.com' + hyperlink.get('href')
        years_q.put(full_link)
    
