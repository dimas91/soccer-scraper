from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import cssutils

from competitionscraper import CompetitionScraper

class BundesligaScraper(CompetitionScraper):
    base_url = 'https://www.bundesliga.com/'

    def get_competition_json(self):
        competition = { 'name': 'Bundesliga' }

        try:
            self.driver.get('https://www.bundesliga.com/en/bundesliga/table')
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            competition['image_url'] = ''
            table = page.find('tbody')
            club_rows = table.find_all('tr')

            if self.verbose:
                print('Found', len(club_rows) - 1, 'clubs.')

            competition['clubs'] = []
            for club in club_rows[1:]:
                url = club.find('a')['href'] + '/squad'
                competition['clubs'].append(self.get_club_data(BundesligaScraper.base_url + url))

            self.driver.close()
            self.driver.quit()
        except Exception as ex:
            print('Something went wrong:', str(ex))
            self.driver.close()
            self.driver.quit()
        return competition

    def get_club_data(self, url, initial_data = None):
        if self.verbose:
            print('Scraping club url:', url)
        
        club_data = {}

        try:
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Grab club data
            club_data['name'] = page.find(class_ = 'clubName').get_text()
            club_data['url'] = page.find(class_ = 'linkBar').find('a')['href']
            club_data['image_url'] = page.find('clublogo').find('img')['src']
            club_data['stadium'] = page.find(class_ = 'stadiumName').find('div').get_text()

            # Look up player tiles
            player_tiles = page.find_all(class_ = 'playercard')
            if self.verbose:
                print('Found', len(player_tiles), 'player items.')

            club_data['players'] = []

            for tile in player_tiles:
                # Check if the player has a number. If not, he's not in the squad
                number_container = tile.find(class_ = 'playerNumber')
                if number_container is None:
                    continue
                #if number_container is None:
                #    continue

                player = {}
                player['first_name'] = tile.find(class_ = 'names').find('h5').get_text()
                player['last_name'] = tile.find(class_ = 'names').find('h4').get_text()
                player['number'] = number_container.get_text()
                #player['number'] = number_container.get_text()
                player_url = BundesligaScraper.base_url + tile.find('a')['href']
                club_data['players'].append(self.get_player_data(player_url))

            return club_data
        except Exception as ex:
            error = str(ex)
            print('Something went wrong:', str(ex))
            return { 'error': error }

    def get_player_data(self, url, initial_data = None):
        player_data = {}

        if initial_data is not None:
            player_data = initial_data

        try:
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            player_data['first_name'] = page.find(class_ = 'firstName').get_text()
            player_data['last_name'] = page.find(class_ = 'lastName').get_text()
            player_data['position'] = page.find(class_ = 'playerPosition').get_text()

            table = page.find(class_ = 'profiletable').find_all(class_ = 'row')
            player_data['name'] = table[0].find_all('div')[1].get_text()
            player_data['nationality'] = table[1].find('nationality-flags').find('span').get_text().strip()
            player_data['birth_date'] = table[2].find_all('div')[1].get_text().replace('.', '-')
            player_data['height'] = table[4].find_all('div')[1].get_text().replace(' cm', '')
            image_style = page.find(class_ = 'playerImage')['style']
            style = cssutils.parseStyle(image_style)['background-image']
            player_data['image_url'] = style.replace('url(', '').replace(')', '')

            if self.verbose:
                print('Scraped player:', player_data['name'])            
            return player_data
        except Exception as ex:
            error = str(ex)
            print(error)
            return { 'error': error }
