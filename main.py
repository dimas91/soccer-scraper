import json
import time

# Import competitions
from eredivisie import EredivisieScraper
from premierleague import PremierLeagueScraper
from laliga import LaLigaScraper

verbose = True
competitions = []
test = False

# Eredivisie
time_start = time.time()
eredivisie = EredivisieScraper(verbose=verbose)
premierleague = PremierLeagueScraper(verbose=verbose)
laliga = LaLigaScraper(verbose=verbose)

competitions.append(eredivisie.get_competition_json())
competitions.append(premierleague.get_competition_json())
competitions.append(laliga.get_competition_json())
time_end = time.time()
print('Scraping complete in', time_end - time_start, 'seconds')


# Print the result to competitions.json
if not test:
   with open('competitions.json', 'w+') as fp:
      json.dump(competitions, fp)
