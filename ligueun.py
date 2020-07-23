from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from competitionscraper import CompetitionScraper

class LigueUnScraper(CompetitionScraper):
    base_url = 'https://www.ligue1.com'

    def get_competition_json(self):
        competition = {'name': 'Ligue 1'}

        try:
            # Note: Getting the clubs for a season still only gets the clubs of the most recent season
            self.driver.get(LigueUnScraper.base_url + '/clubs/List?seasonId=2019-2020')
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            competition['image_url'] = LigueUnScraper.base_url + page.find(class_ = 'field-headerlogo').find('img')['src']
            clubs = page.find_all(class_ = 'clubs-card')

            competition['clubs'] = []
            for club in clubs:
                initial_data = self.get_club_data_from_main_page(club)
                url = club.find(class_ = 'card-body-buttons').find_all('a')[1]['href'] + '&seasonId=2019-2020'
                competition['clubs'].append(self.get_club_data(LigueUnScraper.base_url + url, initial_data))
            
            self.driver.close()
            self.driver.quit()
        except Exception as ex:
            print('Something went wrong:', str(ex))
            self.driver.close()
            self.driver.quit()
        return competition

    # This methods gets initial club data from the main page, avoind having to visit the stadium link
    def get_club_data_from_main_page(self, container):
        club_data = {}
        club_data['name'] = container.find('h3').get_text()
        club_data['stadium'] = container.find('h4').get_text()
        return club_data

    def get_club_data(self, url, initial_data = None):
        if self.verbose:
            print('Scraping club url:', url)

        club_data = {}

        if initial_data is not None:
            club_data = initial_data
            
        try:
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Grab club data
            socials = page.find(class_ = 'hero-social-iconsList').find('li')    # Check for existence of club url
            if socials is not None:
                club_data['url'] = socials.find('a')['href']
            club_data['badge_url'] = LigueUnScraper.base_url + page.find(id = 'ClubPageLogo')['src']
            club_data['players'] = []

            # Look up player containers
            player_rows = page.find_all(class_ = 'SquadTeamTable-details')

            if self.verbose:
                print('Found', len(player_rows), 'player items.')
            
            for row in player_rows:
                player_data = {}
                player_data['name'] = row.find(class_ = 'SquadTeamTable-playerName').get_text().title()
                player_data['image_url'] = LigueUnScraper.base_url + row.find('img')['src']
                player_data['number'] = row.find(class_ = 'SquadTeamTable-detail--number').get_text()
                
                # Check if the player has a number. If not, he's not in the squad
                if player_data['number'] != '-':
                    player_url = row.find(class_ = 'SquadTeamTable-playerName')['href']
                    club_data['players'].append(self.get_player_data(LigueUnScraper.base_url + player_url, player_data))

            return club_data
        except Exception as ex:
            error = str(ex)
            print('Something went wrong:', error)
            return { 'error': error }

        return club_data
    
    def get_player_data(self, url, initial_data = None):
        try:
            player_data = {}

            if initial_data is not None:
                player_data = initial_data
            
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            profile_data = page.find(class_ = 'profile-data').find_all('li', recursive = False)

            # If position is not in player profile data, find the latest position from history
            position = profile_data[1].find(class_ = 'value').get_text()
            if position == '':
                stats_table = page.find(class_ = 'player-stats-table-body').find_all(class_ = 'slick-slide')
                positions = list(map(lambda x: x.find(class_ = 'poste').get_text(), stats_table))
                for pos in positions:
                    if pos != '':
                        position = pos
                        break
            player_data['position'] = position
            player_data['nationality'] = profile_data[3].find(class_ = 'value').get_text()
            player_data['birth_date'] = profile_data[5].find(class_ = 'value').get_text()
            player_data['height'] = profile_data[7].find(class_ = 'value').get_text()
            player_data['weight'] = profile_data[8].find(class_ = 'value').get_text()

            if self.verbose:
                print('Scraped player:', player_data['name'])
            return player_data
        except Exception as ex:
            error = str(ex)
            print(error)
            return { 'error': error }