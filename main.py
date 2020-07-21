import json
import time

# Import competitions
from eredivisie import EredivisieScraper
from premierleague import PremierLeagueScraper
from laliga import LaLigaScraper

verbose = True
competitions = []
test = False
time_start = time.time()

scrapers = {
   'eredivisie': EredivisieScraper(verbose=verbose),
   'premierleague': PremierLeagueScraper(verbose=verbose),
   'laliga': LaLigaScraper(verbose=verbose),
}

for name, scraper in scrapers.items():
   try:
      competitions.append(scraper.get_competition_json())
   except Exception as ex:
      print('Couldn\'t scrape', name, ':', str(ex))

time_end = time.time()
print('Scraping complete in', time_end - time_start, 'seconds')

# Print the result to competitions.json
if not test:
   with open('competitions.json', 'w+') as fp:
      json.dump(competitions, fp)
