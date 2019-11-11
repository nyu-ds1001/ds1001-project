# Web scraping from Baseball-reference.com

In order to scrape data from [Baseball Reference](www.baseball-reference.com), we utilized a `multiprocessing` approach. The initial link was a list of all teams in the MLB, which was downloaded using the `requests` library and parsed using `BeautifulSoup4` to collect the individual team links. Each of these was in turn downloaded and parsed to gather the year-by-year team links, which contained the list of all games played that year for a team.

For each of the game links, we used `bs4` to select specific elements of the page and associate their values with variables. The process of finding a page element (such as a `div`) and parsing it was done using a browser's Inspect Element feature as well as a Jupyter Notebook to receive immediate feedback on whether the parsing was working.

Selecting the data to extract from each page was done in a group meeting in which we discussed what might be possible factors that influence a game's score or result. We settled for:

- weather data
- matchup data (who, when, where)
- team aggregate stats
- starting pitcher aggregate stats

The matchup data was taken from a page header. The team and pitcher aggregate stats were taken from a summary table for the game. The weather data was taken as text from a commented-out section of the HTML (which un-comments itself dynamically when the page is loaded in a browser). For some of this task, the Python regex library `re` was also useful, since it allowed us to find specific text patterns.

This parsing of game links is the most computationally intense part of the scraping process, since it gathers data from 4 different tables, as well as header information and information contained in two commented-out sections of the HTML code. This is where we used `multiprocessing`: By separating the task into an atomic function, we can create several different processes that each run the function on a different link, taken from a Python `multiprocessing.Queue` object.

The results are returned in a different `multiprocessing.Queue` object. Here we also utilized a different process to write the elements from this queue into a file, so that we wouldn't have any issues with concurrent writes to file.

A possible improvement to this approach would be to place the game link in a `set` object and check whether that link has already been downloaded and parsed. This would eliminate double-parsing of a page (stemming from the game being listed on both the home and the away team's pages), which would improve the runtime by approximately half. The caveat to this is that the `set` manipulation would have to be done carefully since one of the parallel processes might be halfway through parsing a page when a process checks if the page has already been parsed. An alternate way of doing this would be using a sort of mixed `set` and `Queue` object which only allows unique values to be placed in the queue.

One overseen thing is that the scraping does not include the starting pitcher's name. Thankfully, the odds data that was scraped does contain the starting pitcher's name, so it was not necessary for us to scrape again.

In total, we scraped 162 games per year, for 30 teams, for 20 years (from 2000 to 2019), which yields 97200 rows of data. All in all, it took about two hours to scrape on a 12-core machine with a 200Mbit/s download ethernet connection.
