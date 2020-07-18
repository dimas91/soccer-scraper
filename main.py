import json
import time

# Import competitions
from eredivisie import EredivisieScraper

verbose = True
competitions = []

# Eredivisie
time_start = time.time()
eredivisie = EredivisieScraper(verbose)
competitions.append(eredivisie.get_competition_json())
time_end = time.time()
print('Scraping complete in', time_end - time_start, 'seconds')


# Print the result to competitions.json
with open('competitions.json', 'w+') as fp:
   json.dump(competitions, fp)