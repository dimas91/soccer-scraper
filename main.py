import json
import time

# Import competitions
from eredivisie import EredivisieScraper
from premierleague import PremierLeagueScraper
from laliga import LaLigaScraper
from ligueun import LigueUnScraper 

verbose = True
competitions = []
test = False
time_start = time.time()

scrapers = {
   'eredivisie': EredivisieScraper(verbose=verbose),
   'premierleague': PremierLeagueScraper(verbose=verbose),
   'laliga': LaLigaScraper(verbose=verbose),
   'ligue1': LigueUnScraper(verbose=verbose),
}

for name, scraper in scrapers.items():
   try:
      competition = scraper.get_competition_json()
      competitions.append(competition)
      with open(name + '.json', 'w+') as fp:
         json.dump(competition, fp)

   except Exception as ex:
      print('Couldn\'t scrape', name, ':', str(ex))

time_end = time.time()
print('Scraping complete in', time_end - time_start, 'seconds')

# Print the result to competitions.json
if not test:
   with open('competitions.json', 'w+') as fp:
      json.dump(competitions, fp)
