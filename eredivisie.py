from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from competitionscraper import CompetitionScraper

class EredivisieScraper(CompetitionScraper):
    deep_player_data = True     # Set this to false to stop from going to individual player pages

    def get_competition_json(self):
        competition = { 'name': 'Eredivisie' }
        self.driver.get('https://eredivisie.nl/nl-nl/Clubs')
        competition_page = BeautifulSoup(self.driver.page_source, 'html.parser')
        clubs = competition_page.find_all(class_ = 'clubs-list__club')
        club_urls = list(map(lambda x: x['href'], clubs))
        if self.verbose:
            print('Found', len(club_urls), 'clubs.')
        competition['clubs'] = list(map(self.get_club_data, club_urls))
        return competition

    def get_club_data(self, club_url):
        if self.verbose:
            print('Scraping club url:', club_url)
        club_data = {}
        self.driver.get(club_url)
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_id('playercontainer').is_displayed())
        club_page = BeautifulSoup(self.driver.page_source, 'html.parser')
        club_data['name'] = club_page.find(id = 'clubname').get_text()
        club_data['badge_url'] = club_page.find(class_ = 'club-img').find('img')['src']
        club_player_items = club_page.find(class_ = 'club-stats__selection__list').find_all(recursive=False)
        if self.verbose:
            print('Found', len(club_player_items), 'player items.')
        club_data['players'] = list(map(self.get_player_data, club_player_items))
        return club_data
        
    def get_player_data(self, list_item):
        player_data = {}
        url = list_item.find('a', { 'class' : 'club-stats__selection__name' })['href']
        player_data['id'] = url.split('/')[-1:]
        player_data['name'] = list_item.find('a', { 'class' : 'club-stats__selection__name' }).get_text()
        player_data['number'] = list_item.find('span', { 'class' : 'club-stats__selection__jerseynr' }).get_text()
        player_data['position'] = list_item.find('span', { 'class' : 'club-stats__selection__position' }).get_text()

        if EredivisieScraper.deep_player_data:
            url = list_item.find('a', { 'class' : 'club-stats__selection__name' })['href']
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            player_data['nationality'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playernationality').get_text()
            player_data['date_of_birth'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerbirth').get_text()
            player_data['height'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerlength').get_text().replace(' CM', '')
            player_data['weight'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerweight').get_text().replace(' KG', '')
            player_data['image_url'] = page.find(id = 'dnn_ctr1102_Dispatch_ctl00_playerimgUrl')['style'].replace('background-image:url(\'', '').replace('\');', '')

        if self.verbose:
            print(player_data['name'], player_data['number'], player_data['position'], player_data['image_url'])
        return player_data