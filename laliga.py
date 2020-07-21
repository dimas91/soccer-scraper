from bs4 import BeautifulSoup
from selenium import webdriver
from competitionscraper import CompetitionScraper

class LaLigaScraper(CompetitionScraper):
    base_url = 'https://www.laliga.com'

    def get_competition_json(self):
        competition = { 'name': 'LaLiga'}

        # Sort of conform to crawl delay while also giving plenty of time for js to load stuff
        self.driver.implicitly_wait(3)
        
        try:
            self.driver.get(LaLigaScraper.base_url + '/en-GB/laliga-santander/clubs')
            page = BeautifulSoup(self.driver.page_source, 'html.parser')
            clubs = page.find_all(class_ = 'styled__ItemContainer-sc-1el5vkx-2')
            club_urls = list(map(lambda club: LaLigaScraper.base_url + club.find('a')['href'], clubs))
            competition['clubs'] = list(map(self.get_club_data, club_urls))
            self.driver.close()
            self.driver.quit()
        except Exception as ex:
            print('Something went wrong:', str(ex))
            self.driver.close()
            self.driver.quit()
        return competition
    
    def get_club_data(self, url):
        if self.verbose:
            print('Scraping club url:', url)
        try:
            club_data = {}
            self.driver.get(url)

            # Hit the squad button to show the squad
            squad_button_xpath = '//button[text()="Squad"]'
            button = self.driver.find_element_by_xpath(squad_button_xpath)
            self.driver.execute_script('arguments[0].click();', button)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Grab club data
            club_data['name'] = page.find(class_ = 'styled__ClubInfoText-wi838o-3').find('h1').get_text()
            club_info = page.find(class_ = 'styled__ClubInfoTextData-wi838o-4').find('tbody').find_all('tr', recursive = False)
            club_data['stadium'] = club_info[1].find_all('p')[1].get_text()
            club_data['url'] = club_info[3].find('a')['href']
            club_data['badge_url'] = page.find(class_ = 'styled__ImgShield-x1xxh6-1')['src']

            # Look up player containers
            player_containers = page.find_all(class_ = 'styled__SquadPlayerCardContainer-sc-1bk5dxm-0')
            player_containers = filter(lambda x: x.find('a') is not None, player_containers)    # Filter out containers without url
            player_urls = list(map(lambda x: LaLigaScraper.base_url + x.find('a')['href'], player_containers))
            if self.verbose:
                print('Found', len(player_urls), 'player items.')
            club_data['players'] = list(filter(lambda player: player is not None, map(self.get_player_data, player_urls)))  # Remove None players (coaching staff)

            return club_data
        except Exception as ex:
            error = str(ex)
            print('Something went wrong:', error)
            return { 'error': error }

    def get_player_data(self, url):
        try:
            player_data = {}
            has_image = True
            self.driver.get(url)
            page = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Check if player has image
            if page.find(class_ = 'styled__PlayerAvatarImg-rwa3kw-20').find('img')['src'] == '(unknown)':
                has_image = False

            position = page.find(class_ = 'styled__PlayerAvatarPathItem-rwa3kw-25 HbVki').find('p').get_text()

            # Skip player if it's not actually a player :)
            if position == 'Trainer' or position == 'Assistant coach':
                return

            player_data_area = page.find(class_ = 'styled__PlayerDataArea-rwa3kw-4 eFwlEv').find_all('div', recursive = False)[1].find_all('div', recursive = False)

            # Get player data
            player_data['name'] = page.find(class_ = 'styled__FirstName-rwa3kw-9').find('p').get_text()
            player_data['nice_name'] = page.find(class_ = 'styled__NiceName-rwa3kw-10').find('h1').get_text()
            player_data['number'] = page.find(class_ = 'styled__ShirtNumber-rwa3kw-11').find('p').get_text()
            player_data['position'] = position
            player_data['nationality'] = page.find(class_ = 'styled__FlagContainer-sc-139pgtl-0').find('img')['title']
            player_data['birth_date'] = player_data_area[0].find('div').find_all('div', recursive = False)[1].find('p').get_text()
            player_data['height'] = player_data_area[2].find('div').find_all('div', recursive = False)[1].find('p').get_text().replace(' cm', '')
            player_data['weight'] = player_data_area[3].find('div').find_all('div', recursive = False)[1].find('p').get_text().replace(' kg', '')
            if has_image:
                player_data['image_url'] = page.find(class_ = 'styled__PlayerAvatarImg-rwa3kw-20').find('img')['src']

            if self.verbose:
                print('Scraped player:', player_data['name'])
            return  player_data
        except Exception as ex:
            error = str(ex)
            print(error)
            return { 'error': error }