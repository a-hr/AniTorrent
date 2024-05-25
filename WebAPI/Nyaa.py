import re
import asyncio
import aiohttp
from math import ceil
from typing import List, Tuple, Union

import requests
import yaml
from bs4 import BeautifulSoup

from time import perf_counter_ns

from TorrentHandler import Torrent


class Nyaa:
    def __init__(self):
        self.base_url = "https://nyaa.si"

        self.search_results = []
        self.groups = self.__parse_groups()
        self.group = ""

    # entrypoint
    async def search(self, term: str, group: str, subcategory: str) -> List[dict]:
        """
        Searches nyaa.si for the given term, group, and subcategory.

        :param term: the query term
        :param group: the uploader group
        :param subcategory: either "english" or "raw"
        :return:
        """
        category = 1
        subcategory = {"english": 2, "raw": 4}[subcategory]

        # check if group is valid
        if group not in self.groups:
            raise ValueError(f"Invalid group: {group}")
        self.group = group

        # first page url, inside the user's group
        url = f"{self.base_url}/user/{group}?c={category}_{subcategory}&q={term}"
        soup, n_pages = self.__get_first_page(url)

        # if one page, parse and return
        if n_pages == 1:
            return self.__parse_results([soup])

        # otherwise, get the rest of the pages asynchronously
        urls = [f"{url}&p={page}" for page in range(1, n_pages + 1)]
        tasks = [self.fetch_async(url) for url in urls]
        responses = await asyncio.gather(*tasks)

        # parse the pages
        pages = [BeautifulSoup(response, "html.parser") for response in responses]
        return self.__parse_results(pages)

    # page download
    def __get_first_page(self, url: str) -> Tuple[BeautifulSoup, int]:
        """
        Gets the first page of the search results.

        :param url: the url to get
        :return: the page and the number of pages
        """
        page = self.__get_page(url)
        # parse and get the number of pages
        pagination = page.find("div", {"class": "pagination-page-info"})
        num_entries = int(re.search(r"^.*out of (\d+) results.*", pagination.text).group(1))
        num_pages = ceil(num_entries / 75)
        return page, num_pages

    @staticmethod
    def __get_page(url: str) -> BeautifulSoup:
        """
        Gets the page at the given url.

        :param url: the url to get
        :return: the page
        """
        response = requests.get(url)
        return BeautifulSoup(response.text, "html.parser")

    @staticmethod
    async def fetch_async(url) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    # page parsing
    def __parse_results(self, pages: List[BeautifulSoup]) -> Tuple:
        """
        Parses the given pages and adds the results to the search_results list.

        :param pages: the pages to parse
        :return: None
        """
        eps: List[Torrent] = []

        for page in pages:
            _eps = [
                self.__parse_title(ep.findChildren()[-1].text.strip()) for ep in page.find_all("td", colspan="2")
            ]
            _mags = [
                link.parent["href"] for link in page.find_all("i", class_="fa fa-fw fa-magnet")
            ]

            [tor.add_magnet(mag) for tor, mag in zip(_eps, _mags) if tor is not None]

            eps.extend(_eps)

        return eps

    def __parse_title(self, title: str) -> Union[dict, None]:
        pattern = self.groups[self.group][0]  # series
        _match = re.search(pattern, title)

        if _match is None:
            # batch
            pattern = self.groups[self.group][1]
            _match = re.search(pattern, title)

            if _match:
                return Torrent(
                    **_match.groupdict() | {
                        "batch": True,
                        "raw_title": title
                        }
                    )
            return None  # unknown structure
        return Torrent(
            **_match.groupdict() | {
                "batch": False,
                "raw_title": title
                }
            )

    # resource parsing
    @staticmethod
    def __parse_groups() -> dict:
        with open("WebAPI/groups.yaml") as file:
            return yaml.safe_load(file)


if __name__ == "__main__":
    # n = Nyaa()
    # loop = asyncio.get_event_loop()
    # t1 = perf_counter_ns()
    # titles = loop.run_until_complete(n.search("oshi", "subsplease", "english"))
    # t2 = perf_counter_ns()
    # print(f"Time: {(t2 - t1) / 1e9}s")
    # print(*titles, sep="\n")
    pass
