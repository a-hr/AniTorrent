import cloudscraper
import requests
import re

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from pathlib import Path

from models import Episode


class SubsPlease:
    
    series_search_url = 'https://subsplease.org/shows/'
    series_search_tag = 'div'
    series_search_flags = 'all-shows-link'
    nyaa_code = 'subsplease'
    bypass_needed = False

    def update_schedule():

        schedule_url = 'https://subsplease.org/api/?f=schedule&tz=Europe/Madrid'
        data = requests.get(schedule_url).json()['schedule']
        schedule = []
        trash = ('Link Click',)

        schedule = [
            [(series['title'], series['time']) 
            for series in data[day] if series['title'] not in trash]
            for day in data]
            
        return schedule

    def extractor(raw_name, magnet_link=None):
        title = str()
        parent_name = str()
        quality = str()

        raw_name = raw_name.strip()
        name_suffix = Path(raw_name).suffix
        title = Path(raw_name).stem

        bracket_text = re.findall(r"\[.*?\]", raw_name)
        parenthesis_text = re.findall(r"\(.*?\)", raw_name)
        quality = parenthesis_text[-1][1:-1]
        [bracket_text.append(element) for element in parenthesis_text]

        for tag in bracket_text:
            title = title.replace(tag, '')

        title = title.strip()

        if '[Batch]' in raw_name:
            parent_name = title.rsplit('-', 1)[0]
            episode_str = parenthesis_text[0]
            episode_int = int(parenthesis_text[0].rsplit('-')[-1][:-1])
            batch=True

        else:
            parent_name, num_str = title.rsplit('-', 1)

            try:
                episode_int = int(num_str)
                episode_str = num_str.strip()
                batch=False
            except:
                title = '-'.join((parent_name, num_str))
                episode_str = num_str.strip()
                episode_int = None
                batch = True

        parent_name = parent_name.strip()

        return Episode(
                    title=title,
                    suffix=name_suffix,
                    series_name=parent_name,
                    quality=quality,
                    episode_str=episode_str,
                    episode_int=episode_int,
                    batch=str(batch),
                    magnet_link=magnet_link
                )


class EraiRaws:

    series_search_url = 'https://www.erai-raws.info/anime-list/'
    series_search_tag = 'div'
    series_search_flags = 'ind-show button button5'
    nyaa_code = 'Erai-raws'
    bypass_needed = True

    def update_schedule():

        link = 'https://www.erai-raws.info/schedule/#Today'
        days = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
            }
        scraper = cloudscraper.create_scraper(
            interpreter='native',
            )
        scraper.headers['Referer'] = 'https://www.erai-raws.info/'
        response = scraper.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        schedule = {
            serie.find('h4', class_='alphabet-title').text.strip():EraiRaws._format_schedule(serie)
            for serie in soup.find_all(
                'div', class_='col-12 col-sm-12 col-md-12 col-lg-12 emain era_center'
                )
            }

        today_soup = soup.find(
            'div', class_='col-12 col-sm-12 col-md-12 col-lg-12 emain era_center_yel'
            )

        today_day = today_soup.find(
            'h4', class_='alphabet-title'
            ).text.replace('(Today)','').replace('\ufeff','').strip()

        schedule[today_day] = EraiRaws._format_schedule(today_soup)

        return [schedule[days[day_n]] for day_n in range(7)]

    def extractor(raw_name, magnet_link=None):
        title = str()
        parent_name = str()
        quality = str()

        quality_list = ['1080p', '720p', '540p', '480p']

        episode_str = ''
        episode_int = int()

        raw_name = raw_name.strip()
        name_suffix = Path(raw_name).suffix
        title = Path(raw_name).stem

        if name_suffix:
            batch = False

        else:
            batch = True

        bracket_text = re.findall(r"\[.*?\]", raw_name)

        if 'p' in bracket_text[1]:
            for quality_type in quality_list:
                if quality_type in bracket_text[1]:
                    quality = quality_type
                    break
        
        elif 'p' in bracket_text[2]:
            for quality_type in quality_list:
                if quality_type in bracket_text[2]:
                    quality = quality_type
                    break

        for bracket in bracket_text:
            title = title.replace(bracket, '')

        if batch:
            parent_name, num_str = title.strip().rsplit('-', 1)
            episode_str = num_str.strip()
            episode_int = None
        
        else:
            parent_name, num_str = title.strip().rsplit('-', 1)
            episode_str = num_str.strip()
            try:
                episode_int = int(num_str.replace('END', ''))
            except:
                episode_str = 'Movie/OVA'
        
        parent_name = parent_name.strip()
        title = title.strip()

        return Episode(
                    title=title,
                    suffix=name_suffix,
                    series_name=parent_name,
                    quality=quality,
                    episode_str=episode_str,
                    episode_int=episode_int,
                    batch=str(batch),
                    magnet_link=magnet_link
                )

    @staticmethod
    def _format_schedule(soup_object):
        schedule = []

        times_raw_list = [
            time.text.strip() 
            for time in soup_object.find_all('span', class_='cccccc')]
        series_raw_list = [
            time.parent.a.text.strip() 
            for time in soup_object.find_all('span', class_='cccccc')]

        for serie, time in zip(series_raw_list, times_raw_list):
            hora = datetime.strptime(time, '%H:%M %p') + timedelta(hours = 9)
            schedule.append((serie, f"{hora.hour}:{str(hora.minute).ljust(2, '0')}"))
        
        return schedule