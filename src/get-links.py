#! /usr/bin/env python3
"""
Find all player links in BaseballReference.com by using the index pages.
Since we only have 26 links to download and parse, we're not going to use
multiprocessing.
"""

import string
import sys
from os import path
import requests
from bs4 import BeautifulSoup


# all index pages follow the same format:
# https://www.baseball-reference.com/players/$a/
# where $a is a letter from "a" to "z".

index_links = ['https://www.baseball-reference.com/players/{}/'.format(x)
               for x in string.ascii_lowercase]

link_count = len(index_links)
results = []

for i, link in enumerate(index_links):
    page = requests.get(link)

    if page.status_code != 200:
        sys.exit()

    soup = BeautifulSoup(page.text, 'html.parser')

    section = soup.find('div', id='all_players_')

    for hyperlink in section.find_all('a'):
        full_link = 'http://www.baseballreference.com' + hyperlink.get('href')
        results.append(full_link)

    print('\r{}/{} parsed'.format(i + 1, link_count), end='', flush=True)

# one folder up, into the 'data' folder
current_dir = path.dirname(path.abspath(__file__))
file_loc = path.join(current_dir, '..', 'data', 'player_links.txt')

with open(file_loc, 'w') as f:
    f.write('\n'.join(results))
