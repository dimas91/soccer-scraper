from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from competitionscraper import CompetitionScraper

class LigaNOSScraper(CompetitionScraper):
    base_url = 'https://www.ligaportugal.pt'

    def get_competition_json(self):
        competition = { 'name': 'Liga NOS' }
        try:
            self.driver.get('https://www.ligaportugal.pt/en/liga/clube/20192020/liganos')
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            competition['image_url'] = LigaNOSScraper.base_url + page.find(id = 'MENU_KEY_COMPETITION_1-nav').find('img')['src']
            clubs = page.find(class_ = 'subnav-main-teams').find_all('a')
            competition['clubs'] = list(map(self.get_club_data, clubs))
            return competition
        except Exception as ex:
            print('Something went wrong:', str(ex))
        finally:
            self.driver.close()
            self.driver.quit()
    
    def get_club_data(self, club_container):
        club_data = {}
        club_data['name'] = club_container.get_text().strip()
        club_url = LigaNOSScraper.base_url + club_container['href']
        if self.verbose:
            print('Scraping club url:', club_url)
        try:
            self.driver.get(club_url)
            squad_button_xpath = '//a[text()="Squad"]'
            button = self.driver.find_element_by_xpath(squad_button_xpath)
            self.driver.execute_script('arguments[0].click();', button)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            player_container = page.find(id = 'players')
            player_table = player_container.find('table')
            player_rows = player_table.find('tbody').find_all('tr', recursive = False)
            if self.verbose:
                print('Found', len(player_rows), 'player items.')

            header = page.find(class_ = 'page-header-team')
            club_data['stadium'] = header.find('p').get_text()
            club_data['players'] = list(map(self.get_player_data, player_rows))
            return club_data
        except Exception as ex:
            error = str(ex)
            print('Something went wrong:', str(ex))
            return { 'error': error }
    
    def get_player_data(self, container):
        try:
            player_data = {}

            # Get player data
            cells = container.find_all('td', recursive = False)
            
            player_data['number'] = cells[0].get_text()
            player_data['position'] = cells[3].get_text()
            player_data['nationality'] = cells[4].get_text()
            player_data['image_url'] = LigaNOSScraper.base_url + cells[1].find('img')['src']
            player_data['name_short'] = cells[2].get_text().strip()

            url = LigaNOSScraper.base_url + container['data-detail']
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            header = page.find(class_ = 'page-header-info')
            info = header.find_all('p', recursive = False)[1].get_text().split(' | ')
            player_data['name'] = info[0]
            player_data['birth_date'] = '-'.join(info[2].split(' ')[0].split('/')[::-1])

            if self.verbose:
                print('Scraped player:', player_data['name'])
            return  player_data
        except Exception as ex:
            error = str(ex)
            print(error)
            return { 'error': error }