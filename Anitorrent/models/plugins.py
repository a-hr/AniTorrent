import re
from abc import ABC, abstractmethod
from functools import lru_cache
from math import ceil
from pathlib import Path

import cloudscraper
import requests
from bs4 import BeautifulSoup

from models import Episode


def match(sample, checkable):
    for chunk in sample.split():
        if not chunk.strip().lower() in checkable.lower():
            return False
    return True


def page_cap(fansub, title):
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


class SubsPlease:

    search_url = "https://subsplease.org/shows/"
    series_search_tag = "div"
    series_search_flags = "all-shows-link"
    nyaa_code = "subsplease"

    def get_series_list(title: str):
        return [serie for serie in SubsPlease.__get_list() if match(title, serie)]

    @lru_cache
    def __get_list():
        response = requests.get(SubsPlease.search_url)
        soup = BeautifulSoup(response.content, "html.parser")

        return [
            serie.text.strip()
            for serie in soup.find_all(
                SubsPlease.series_search_tag, class_=SubsPlease.series_search_flags
            )
        ]

    def parser(text: str, magnet_link=None, expected=None) -> list:
        text = text.removeprefix("[SubsPlease]")
        r = re.findall("\[(.*?)\]", text.strip())
        batch = True if (code := r[0]) == "Batch" else False
        clean_text = text.replace(f"[{code}]", "").replace("v1", "").replace("v2", "")

        if batch:
            par = re.findall("\((.*?)\)", clean_text)
            info, quality = par[1:] if len(par) > 2 else par
            title = (
                clean_text.replace(f"({info})", "").replace(f"({quality})", "").strip()
            )

            return Episode(
                title=title,
                suffix="",
                series_name=title,
                quality=quality,
                info=info,
                multi="False",
                episode_int=None,
                batch=str(batch),
                magnet_link=magnet_link,
            )
        else:
            parent, ep, quality = re.findall(
                "(.*?).-.([0-9\.]*).\(([0-9]*p)\)", clean_text
            )[0]

            try:
                ep = int(ep)
            except ValueError:
                ep = float(ep)

            return Episode(
                title=f"{parent} - {ep}",
                suffix=clean_text[-4:],
                series_name=parent,
                quality=quality,
                info="",
                multi="False",
                episode_int=ep,
                batch=str(batch),
                magnet_link=magnet_link,
            )


class EraiRaws:

    search_url = "https://www.erai-raws.info/anime-list/"
    series_search_tag = "div"
    series_search_flags = "ind-show button button5"
    nyaa_code = "Erai-raws"

    def get_series_list(title: str):
        return [serie for serie in EraiRaws.__get_list() if match(title, serie)]

    @lru_cache
    def __get_list():
        scraper = cloudscraper.create_scraper(interpreter="native")
        scraper.headers["Referer"] = "https://www.erai-raws.info/"
        response = scraper.get(EraiRaws.search_url)
        soup = BeautifulSoup(response.content, "html.parser")

        return [
            serie.text.strip()
            for serie in soup.find_all(
                EraiRaws.series_search_tag, class_=EraiRaws.series_search_flags
            )
        ]

    def parser(text: str, magnet_link=None, expected=None) -> Episode:
        text = re.sub("\[...?\]| END", "", text).replace(
            "[Erai-raws]", ""
        )  # clean [v0]/[VRV]/[BD]
        multi, info = "", ""

        if len(r := re.findall("\[(.*?)\]", text)) == 2:
            multi = True if "Mu" in r[1] else False
            text = text.replace(f"[{r[1]}]", "")

        text = text.replace(f"[{r[0]}]", "")
        quality = re.findall("(.*?p)", r[0])[0]
        batch = True if not (suffix := Path(text).suffix) else False
        text = text.replace(suffix, "")

        if "OVA" in text:
            info = "OVA"
            series_name, ep = re.findall("(.*) - ([0-9]*)", text)[0]
            title = f"{series_name} - {ep}" if ep else series_name.removesuffix(".")
        elif not batch:
            series_name, ep = re.findall("(.*) - ([0-9]*)", text)[0]
            title = f"{series_name} - {ep}"
        else:
            series_name, info = re.findall(
                "(.*) - ([0-9]* - [0-9]*)", text.replace("~", "-")
            )[0]
            title, ep = series_name, None

        return Episode(
            title=title,
            suffix=suffix,
            series_name=series_name,
            quality=quality,
            info=info,
            multi=str(multi),
            episode_int=ep,
            batch=str(batch),
            magnet_link=magnet_link,
        )


class Judas:

    search_url = "https://nyaa.si/user/Judas?f=0&c=1_2&q={}&p={}"
    nyaa_code = "Judas"

    @lru_cache
    def get_series_list(title: str):
        series = set([None])
        cap, first_content = page_cap(Judas.nyaa_code, title)
        series.union(Judas.__soup_parser(first_content))

        for page in range(1, cap + 1):
            url = Judas.search_url.format(title, page)
            response = requests.get(url).content
            series = series.union(Judas.__soup_parser(response))

        series.remove(None)
        return list(series)

    def __soup_parser(content):
        soup = BeautifulSoup(content, "html.parser")
        return {
            Judas.__parent_parser(episode.findChildren()[-1].text.strip())
            for episode in soup.find_all("td", colspan="2")
        }

    def __parent_parser(title):
        if res := re.findall("\[Judas\] (.*?) \(Season|\[Judas\] (.*?) - .*?", title):
            return res[0][0] if res[0][0] else res[0][1]
        else:
            return None

    def parser(text, magnet_link=None, expected=None) -> Episode:
        "if (Seasons or (Complete Series Batch) -> dont rename"
        " if [UNCENSORED -> info = '+18'"
        " if [Multi-Subs] -> multi = True"
        " (Season'espacio' or (Batch)-> batch = True"
        "(Weekly) -> batch = False"

        text = re.sub("\[...?\]| END", "", text)  # clean [v0]/[VRV]/[BD]
        multi, info = "", ""

        if len(r := re.findall("\[(.*?)\]", text)) == 2:
            multi = True if "Mu" in r[1] else False
            text = text.replace(f"[{r[1]}]", "")

        text = text.replace(f"[{r[0]}]", "")
        quality = re.findall("(.*?p)", r[0])[0]
        batch = True if not (suffix := Path(text).suffix) else False
        text = text.replace(suffix, "")

        if "OVA" in text:
            info = "OVA"
            series_name, ep = re.findall("(.*) - ([0-9]*)", text)[0]
            title = f"{series_name} - {ep}" if ep else series_name.removesuffix(".")
        elif not batch:
            series_name, ep = re.findall("(.*) - ([0-9]*)", text)[0]
            title = f"{series_name} - {ep}"
        else:
            series_name, info = re.findall(
                "(.*) - ([0-9]* - [0-9]*)", text.replace("~", "-")
            )[0]
            title, ep = series_name, None

        return dict(
            title=title,
            suffix=suffix,
            series_name=series_name,
            quality=quality,
            info=info,
            multi=str(multi),
            episode_int=ep,
            batch=str(batch),
            magnet_link=magnet_link,
        )


class HorribleSubs:

    search_url = "https://nyaa.si/user/HorribleSubs?f=0&c=1_2&q={}&p={}"
    nyaa_code = "HorribleSubs"

    @lru_cache
    def get_series_list(title: str):
        url, series = HorribleSubs.search_url.format(title, 1), set((None,))
        while url:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            _series = {
                HorribleSubs.__parent_parser(episode.findChildren()[-1].text.strip())
                for episode in soup.find_all("td", colspan="2")
            }
            try:
                url = "https://nyaa.si" + soup.find("li", class_="next").a["href"]
            except:
                url = None
            finally:
                series = series.union(_series)

        series.remove(None)
        return list(series)

    def __parent_parser(title):
        if res := re.findall(
            "\[HorribleSubs\] (.*?) \(\d|\[HorribleSubs\] (.*?) - .*?", title
        ):
            return res[0][0] if res[0][0] else res[0][1]
        else:
            return None

    def parser(raw_name, magnet_link=None, expected=None) -> Episode:
        raw_name = raw_name.replace("[HorribleSubs]", "")
        if "(Batch)" in raw_name:
            batch = True
            suffix = ""
            ep = None
            series_name, info, quality = re.findall(
                "(.*?) \(([0-9]*?-[0-9]*?)\) \[(.*?)\]", raw_name
            )
            title = series_name

        else:
            batch = False
            suffix = ".mkv"
            info = ""
            series_name, ep, quality = re.findall(
                "(.*?) - ([0-9]*?) \[(.*?)\]", raw_name
            )[0]
            title = f"{series_name} - {ep}"

        return Episode(
            title=title,
            suffix=suffix,
            series_name=series_name,
            quality=quality,
            info=info,
            multi="False",
            episode_int=ep,
            batch=str(batch),
            magnet_link=magnet_link,
        )


# TODO: standarize plugins subclassing base plugin
class BasePlugin(ABC):
    @abstractmethod
    def get_series_list(title: str):
        ...

    @abstractmethod
    def parser(text: str, magnet_link=None):
        ...
