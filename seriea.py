from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import cssutils

from competitionscraper import CompetitionScraper

class SerieAScraper(CompetitionScraper):
    base_url = 'http://www.legaseriea.it'
    
    def get_competition_json(self):
        competition = { 'name': 'Serie A' }

        try:
            self.driver.get('http://www.legaseriea.it/en')
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            competition['image_url'] = page.find(id = 'logo').find('img')['src']

            header = page.find(id = 'squadre_header')
            club_tiles = header.find('div').find_all('a', recursive = False)

            if self.verbose:
                print('Found', len(club_tiles), 'clubs')
            competition['clubs'] = []
            for club in club_tiles:
                club_data = {}
                club_url = SerieAScraper.base_url + club['href']
                club_data['name'] = club.find('img')['title'].title()
                club_data['image_url'] = SerieAScraper.base_url + club.find('img')['src']
                competition['clubs'].append(self.get_club_data(club_url, club_data))

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

        if initial_data is not None:
            club_data = initial_data

        try:
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            info_sections = page.find(class_ = 'organigramma').find('aside').find_all('section')
            url_sections = info_sections[2].find_all('article')
            url_section = None

            if len(url_sections) == 2:
                url_section = url_sections[1]
            else:
                url_section = url_sections[0]
            
            club_data['url'] = url_section.find('a')['href']

            club_data['stadium'] = info_sections[1].find_all('article')[1].find('p').get_text().title()

            squad_url = url + '/team'
            self.driver.get(squad_url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            player_rows = page.find(id = 'rosa-completa').find('table').find('tbody').find_all('tr')[1:]
            if self.verbose:
                print('Found', len(player_rows), 'player items.')

            club_data['players'] = []
            for row in player_rows:
                club_data['players'].append(self.get_player_data(row))

            return club_data
        except Exception as ex:
            error = str(ex)
            print('Something went wrong:', str(ex))
            return { 'error': error }
    
    def get_player_data(self, container):
        player_data = {}

        try:
            cells = container.find_all('td', recursive = False)
            player_data['name'] = cells[1].find('span').get_text().title().strip()
            player_data['number'] = cells[0].get_text()
            player_data['position'] = cells[3].get_text()
            player_data['nationality'] = cells[4].find('img')['title']
            player_data['birth_date'] = cells[2].get_text().replace('/', '-')

            if self.verbose:
                print('Scraped player:', player_data['name'])   
            return player_data
        except Exception as ex:
            error = str(ex)
            print(error)
            return { 'error': error }
            