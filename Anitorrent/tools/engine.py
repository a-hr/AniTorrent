import requests
import cloudscraper

from bs4 import BeautifulSoup

from models import SubsPlease, EraiRaws

class Engine:

    SEARCH_URL = 'https://nyaa.si/user/{}?f=0&c=0_0&q={}&p=1'
    
    def __init__(self, selected_fansub: str) -> None:
        
        if selected_fansub.replace(' ', '').lower() == 'subsplease':
            self.__dict__.update(SubsPlease.__dict__)
            
        elif selected_fansub.replace(' ', '').lower() == 'erairaws':
            self.__dict__.update(EraiRaws.__dict__)

    def available_series(self):
        
        if not self.bypass_needed:
            response = requests.get(self.series_search_url)
        
        else:
            scraper = cloudscraper.create_scraper(
				interpreter='native',
			)
            scraper.headers['Referer'] = 'https://www.erai-raws.info/'
            response = scraper.get(self.series_search_url)

        soup = BeautifulSoup(response.content, 'html.parser')
        
        return [serie.text.strip() for serie in soup.find_all(
            self.series_search_tag, class_=self.series_search_flags
            )]

    def search_episodes(self, series_name):

        url_safe = lambda input_str: input_str.strip().lower().replace(':',' ').replace(' ','+')     

        search_url = self.SEARCH_URL.format(self.nyaa_code, url_safe(series_name))
        episodes = list()
        magnets = list()
        
        while search_url:
            response = requests.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                search_url = 'https://nyaa.si' + soup.find('li', class_='next').a['href']
            except:
                search_url = None

            [episodes.append(episode.findChildren()[-1].text.strip()) 
                for episode in soup.find_all('td', colspan='2')]

            [magnets.append(link.parent['href']) 
                for link in soup.find_all('i', class_='fa fa-fw fa-magnet')]


        if len(episodes) == len(magnets):
            episode_number = len(episodes)
        else:
            return []

        return [self.extractor(episodes[index], magnets[index])for index in range(episode_number)]
    
    def match(self, sample, checkable):
        for chunk in sample.split():
            if not chunk.strip().lower() in checkable.lower():
                return False

        return True