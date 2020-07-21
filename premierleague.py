from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from competitionscraper import CompetitionScraper

class PremierLeagueScraper(CompetitionScraper):
    def get_competition_json(self):
        competition = { 'name': 'Premier League' }
        try:
            self.driver.get('https://www.premierleague.com/clubs')
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            clubs = page.find_all(class_ = 'indexItem')
            club_urls = list(map(lambda x: 'https://www.premierleague.com' + x['href'], clubs))
            if self.verbose:
                print('Found', len(club_urls), 'clubs.')
            competition['clubs'] = list(map(self.get_club_data, club_urls))
            self.driver.close()
            self.driver.quit()
        except Exception as ex:
            print('Something went wrong:', str(ex))
            self.driver.close()
            self.driver.quit()
        return competition

    def get_club_data(self, club_url):
        club_url = club_url.replace('overview', 'squad')
        if self.verbose:
            print('Scraping club url:', club_url)
        try:
            club_data = {}
            self.driver.get(club_url)
            WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_class_name('playerOverviewCard').is_displayed() and x.find_element_by_class_name('stadium').is_displayed()) # Apparently if this class is there, everything is there
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Grab club data
            club_data['name'] = page.find(class_ = 'js-team').get_text()
            club_data['stadium'] = page.find(class_ = 'stadium').get_text()
            club_data['url'] = page.find(class_ = 'website').find('a')['href'].split('?')[0]
            club_data['badge_url'] = page.find(class_ = 'clubBadgeFallback')['src']
            club_data['badge_url_svg'] = page.find(class_ = 'clubSvg')['srcset']

            club_player_items = page.find(class_ = 'squadListContainer').find_all(class_ = 'playerOverviewCard')
            if self.verbose:
                print('Found', len(club_player_items), 'player items.')
            club_data['players'] = list(map(self.get_player_data, club_player_items))
            return club_data
        except Exception as ex:
            error = str(ex)
            print('Something went wrong:', str(ex))
            return { 'error': error }

    def get_player_data(self, container):
        try:
            player_data = {}
            relative_url = container['href']
            player_data['id'] = relative_url.split('/')[2]
            player_data['name'] = container.find(class_ = 'name').get_text()
            player_data['number'] = container.find(class_ = 'number').get_text()
            player_data['position'] = container.find(class_ = 'position').get_text()
            player_data['nationality'] = container.find(class_ = 'playerCountry').get_text()

            if self.deep_player_data:
                self.driver.get('https://www.premierleague.com' + relative_url)
                WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath('(//img[@data-script="pl_player-image"])[1]').get_attribute('src').startswith('https://'))
                page = BeautifulSoup(self.driver.page_source, 'html.parser')
                data_container = page.find(class_ = 'personalLists')
                if data_container is not None:
                    dob_div = data_container.find(class_ = 'pdcol2').find(class_ = 'info')
                    if dob_div is not None:
                        dob_div.get_text().strip().split(' ')[0]
                    height_div = data_container.find(class_ = 'pdcol3').find(class_ = 'info')
                    if height_div is not None:
                        player_data['height'] = height_div.get_text().replace('cm', '')
                    player_data['image_url'] = page.find(class_ = 'imgContainer').find('img')['src']
            
            if self.verbose:
                print('Scraped player:', player_data['name'])
            return player_data
        except Exception as ex:
            error = str(ex)
            print(error)
            return { 'error': error }
