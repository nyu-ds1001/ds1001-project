import argparse
import asyncio
import csv
import json
import math
import os
import traceback
from datetime import datetime
from itertools import cycle
from random import choice

import requests
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession, HTMLSession

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15'
]

OUTPUT = f"output.csv"
debug = 0

def parse_page(text: str):
    t = text.split('new PageTournament(')[1].split(')')[0]
    js = json.loads(t)
    return js.get('id', ''), js.get('sid', '')


def get(url):
    if debug: print(f'Getting {url}')
    r = requests.get(url, headers={'User-Agent': choice(USER_AGENTS)})
    return r


def write_csv(data, file_name=OUTPUT, mode='a'):
    if debug: print(f'Saving to: {file_name}')
    with open(file_name, mode=mode, encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for row in data:
            writer.writerow(row)


async def scrape_page(url, asession, sem, time_from):
    async with sem:
        if debug: print(f'Checking {url}')
        t = int(datetime.now().timestamp() * 1000)
        params = (('_', t), )

        r = await asession.get(
            url,
            headers={
                'User-Agent': choice(USER_AGENTS),
                'Referer':
                'https://www.oddsportal.com/baseball/usa/mlb/results/'
            },
            params=params)
        path = url.replace('https://fb.oddsportal.com', '').strip()
        text = r.text.split(f"{path}',")[1].strip()[:-2]

        js = json.loads(text)
        html = js.get('d', {}).get('html', '')
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select('tr:not(.table-dummyrow):not(.nob-border)')[1:]
        results = []
        for row in rows:
            tds = row.select('td')
            time = ''.join([
                x for x in tds[0].get('class')
                if 'table-time' not in x and 'datet' not in x
            ]).strip().split('-')[0].replace('t', '')
            dt = datetime.fromtimestamp(int(time))
            if dt >= time_from:
                day = dt.strftime(r'%Y%m%d')
                time = dt.strftime(r'%H:%M')
                teams, odds, _, _, number = [
                    x.text.strip() for x in tds[1:]
                ]
                winner = tds[1].select_one('span.bold')
                winner = winner.text if winner else ''
                team1, team2 = [x.strip() for x in teams.split('-')]
                line1 = format_us(decode_odds(tds[-3].get('xodd', '')))
                line2 = format_us(decode_odds(tds[-2].get('xodd', '')))
                results.append([day, time, team1, team2, odds, line1, line2, number, winner])
        return results


def decode_odds(odds: str):
    if not odds:
        return ''
    odds = odds.replace('a', '1').replace('x', '2').replace('c', '3').replace('t', '4').replace(
                        'e', '5').replace('o', '6').replace('p', '7').replace('z', '.').replace('f', '|')
    splitted_odds = odds.split('|')
    if len(splitted_odds) == 1:
        return float(splitted_odds[0])
    else:
        return float(splitted_odds[1])

def format_us(decimal):
    if type(decimal) != float:
        return 'N/A'
    if decimal >= 2:
        return f'+{math.floor((decimal - 1) * 100)}'
    elif decimal != 1:
        return f'-{round(100 / (decimal - 1))}'
    else:
        return 'N/A'

async def main(year, month, day=1, write=0):
    sem = asyncio.Semaphore(10)
    current_year = datetime.now().year
    time_from = datetime(year, month, day)
    asession = AsyncHTMLSession()

    result = []
    for y in range(year, current_year + 1):
        r = get(f'https://www.oddsportal.com/baseball/usa/mlb/results/' if y ==
                current_year else
                f'https://www.oddsportal.com/baseball/usa/mlb-{y}/results/')

        id, sid = parse_page(r.text)
        tasks = []
        # I can't think of a clean way to check the number of pages, but I don't see any over 60
        for i in range(1, 64):
            tasks.append(
                asyncio.ensure_future(
                    scrape_page(
                        f'https://fb.oddsportal.com/ajax-sport-country-tournament-archive/{sid}/{id}/X0/1/0/{i}/',
                        asession, sem, time_from)))

        for f in asyncio.as_completed(tasks):
            r = await f
            result += r

    if write:
        write_csv([[
            'Day', 'Time', 'Team1', 'Team2', 'Odds', 'Line1', 'Line2', 'Number',
            'Winner']], mode='w')
        write_csv(result)
    else:
        return result

if __name__ == "__main__":
    today = datetime.today()
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', help='Year', default=today.year)
    parser.add_argument('-m', '--month', help='Month', default=today.month)
    args = parser.parse_args()
    asyncio.run(main(int(args.year), int(args.month), write=True))
