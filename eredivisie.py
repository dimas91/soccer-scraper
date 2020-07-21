from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from competitionscraper import CompetitionScraper

class EredivisieScraper(CompetitionScraper):
    def get_competition_json(self):
        competition = { 'name': 'Eredivisie' }

        try:
            self.driver.get('https://eredivisie.nl/nl-nl/Clubs')
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            clubs = page.find_all(class_ = 'clubs-list__club')
            club_urls = list(map(lambda x: x['href'], clubs))
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
        if self.verbose:
            print('Scraping club url:', club_url)
        try:
            club_data = {}
            self.driver.get(club_url)
            WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_id('playercontainer').is_displayed())
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            club_data['name'] = page.find(id = 'clubname').get_text()
            club_data['badge_url'] = page.find(class_ = 'club-img').find('img')['src']
            club_player_items = page.find(class_ = 'club-stats__selection__list').find_all(recursive=False)
            if self.verbose:
                print('Found', len(club_player_items), 'player items.')
            club_data['players'] = list(map(self.get_player_data, club_player_items))
            return club_data
        except Exception as ex:
            error = str(ex)
            print('Something went wrong:', error)
            return { 'error': error }
        
    def get_player_data(self, container):
        try:
            player_data = {}
            url = container.find('a', { 'class' : 'club-stats__selection__name' })['href']
            player_data['id'] = url.split('/')[-1:]
            player_data['name'] = container.find('a', { 'class' : 'club-stats__selection__name' }).get_text()
            player_data['number'] = container.find('span', { 'class' : 'club-stats__selection__jerseynr' }).get_text()
            player_data['position'] = container.find('span', { 'class' : 'club-stats__selection__position' }).get_text()

            if self.deep_player_data:
                url = container.find('a', { 'class' : 'club-stats__selection__name' })['href']
                self.driver.get(url)
                page = BeautifulSoup(self.driver.page_source, 'html.parser')
                player_data['nationality'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playernationality').get_text()
                player_data['date_of_birth'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerbirth').get_text()
                player_data['height'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerlength').get_text().replace(' CM', '')
                player_data['weight'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerweight').get_text().replace(' KG', '')
                player_data['image_url'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerimgUrl')['style'].replace('background-image:url(\'', '').replace('\');', '')

            if self.verbose:
                print('Scraped player:', player_data['name'])
            return player_data
        except Exception as ex:
            error = str(ex)
            print(error)
            return { 'error': error }
