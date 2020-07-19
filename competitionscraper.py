from selenium import webdriver

class CompetitionScraper:
    def __init__(self, verbose=False):
        self.driver = self.get_driver()
        self.verbose = verbose

    def get_driver(self):
        op = webdriver.ChromeOptions()
        op.add_argument('headless')         # Don't open actual browser window
        op.add_argument('--log-level=3')    # Suppress logging
        op.add_experimental_option('excludeSwitches', ['enable-logging'])   # Suppress devtools listening message
        driver = webdriver.Chrome(options=op)
        return driver
    
    def get_competition_json(self):
        return {}
