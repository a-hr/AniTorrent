import json
import re
from datetime import datetime
from functools import lru_cache
from math import ceil

import requests
from bs4 import BeautifulSoup
from models import AiringAnime
from models.plugins import EraiRaws, HorribleSubs, Judas, SubsPlease
from requests import Timeout


class PluginEngine:
    def __init__(self, fansubs=None) -> None:
        FANSUBS = {
            "SubsPlease": SubsPlease,
            "EraiRaws": EraiRaws,
            "HorribleSubs": HorribleSubs,
            "Judas": Judas,
        }

        self.FANSUBS = (
            {fansub: FANSUBS[fansub] for fansub in fansubs} if fansubs else FANSUBS
        )
        self.SEARCH_URL = "https://nyaa.si/user/{}?f=0&c=0_0&q={}&p={}"

    @lru_cache()
    def update_schedule(self, config: object, today: bool = False) -> list[list]:
        """Generates a schedule containing airing anime. Series are
        ordered based on MAL rating on the weekly schedule, and based
        on airing time on the daily schedule.

        Args:
            today (bool, optional): Whether to retrieve weekly or dauly schedule. Defaults to False.

        Returns:
            list[list]: Contains a list for each week day, with AiringAnime objects on them.
        """
        try:
            r = requests.get(f"https://api.jikan.moe/v3/season/", timeout=1).json()["anime"]
        except Timeout:
            with open(config.schedule_backup, 'r') as s:
                r = json.load(s)
        else:
            with open(config.schedule_backup, 'w') as s:
                json.dump(r, s)

        response = [[] for _ in range(7)]
        for anime in r:
            if anime["score"]: # and anime["type"] == "TV" 
                response[(a := AiringAnime(**anime)).airing_day].append(a)

        def rating(anime: AiringAnime) -> float:
            return anime.score if anime.score else 0

        def time_sorter(anime: AiringAnime) -> int:
            hour, minute = anime.airing_time.split(":")
            return int(hour) * 60 + int(minute)

        if today:
            response = sorted(response[datetime.today().weekday()], key=time_sorter)
        else:
            [day.sort(key=rating, reverse=True) for day in response]

        return response

    def select_parser(self, selected_fansub: str) -> object:
        return getattr(self.FANSUBS[selected_fansub], "parser")

    def available_series(self, title) -> dict:
        res = {}
        for fansub, handler in self.FANSUBS.items():
            res[fansub] = handler.get_series_list(title)
        return res

    def search_episodes(self, fansub, title):
        fansub_code = getattr(self.FANSUBS[fansub], "nyaa_code")
        parser, episodes, magnets = self.select_parser(fansub), [], []
        title = title.strip().replace(":", " ").replace(" ", "+").removesuffix(".")
        cap, first_response = self.__page_cap(fansub_code, title)
        episodes, magnets = self.__soup_parser(first_response, episodes, magnets)

        for page in range(2, cap + 1):
            url = self.SEARCH_URL.format(fansub, title, page)
            response = requests.get(url).content
            episodes, magnets = self.__soup_parser(response, episodes, magnets)

        if len(episodes) == len(magnets):
            episode_number = len(episodes)
        else:
            return []
        return [
            res
            for index in range(episode_number)
            if (res := parser(episodes[index], magnets[index]))
        ]

    def __page_cap(self, fansub, title):
        res = requests.get(f"https://nyaa.si/user/{fansub}?f=0&c=1_2&q={title}")
        soup = BeautifulSoup(res.content, "html.parser")
        text = soup.find("div", class_="pagination-page-info").contents[0]
        try:
            partial, total = re.findall(
                "Displaying results 1-(\d*) out of (\d*) results.", text
            )[0]
            return (
                1 if int(partial) > 75 else ceil(int(total) / int(partial)),
                res.content,
            )
        except:
            return (0, b"")

    def __soup_parser(self, response: bytes, episodes: list, magnets: list):
        soup = BeautifulSoup(response, "html.parser")

        [
            episodes.append(episode.findChildren()[-1].text.strip())
            for episode in soup.find_all("td", colspan="2")
        ]

        [
            magnets.append(link.parent["href"])
            for link in soup.find_all("i", class_="fa fa-fw fa-magnet")
        ]

        return episodes, magnets
