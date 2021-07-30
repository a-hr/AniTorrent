import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from random import randint

import qbittorrentapi


class Episode:

    __slots__ = ('title', 'suffix', 'series_name', 'quality', 'episode_str',
                 'episode_int', 'batch', 'magnet', 'info', 'multi')

    def __init__(self, magnet_link, **kwargs) -> None:

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.magnet = magnet_link

    def __str__(self) -> str:
        return f'title: {self.title}, quality: {self.quality}, info: {self.info}'


class Torrent:

    def __init__(self, episode_obj: Episode, __config: object) -> None:

        self.status = ''
        self.progress = 0
        self.eta = 0

        self._port_WebUI = __config.port_WebUI
        self._user_WebUI = __config.user_WebUI
        self._pass_WebUI = __config.pass_WebUI

        self.torrent_hash = ''
        self.magnet = episode_obj.magnet

        self.postprocess = __config.postprocess

        self.parent = episode_obj.series_name.removesuffix('.').strip()
        self.qb_download_path = ''

        self.title = episode_obj.title.strip()
        self.new_name = f'{self.title}{episode_obj.suffix}'
        self.is_folder = True if episode_obj.batch.lower() == 'true' else False

        if self.is_folder:
            self.download_folder = __config.download_path
        else:
            self.download_folder = f'{__config.download_path}/{self.parent}'

        self.tag = f"{self.title[:2]}.{randint(0, 99999999)}"

    def update_progress(self, data) -> bool:

        self.progress = int(data['progress'] * 100)

        if self.progress == 100:
            self.status = 'completed'
            return True

        else:
            self.status = 'downloading'
            self.eta = data['eta']
            self.qb_download_path = data['content_path']
            return False

    def rename(self):

        qbt_client = qbittorrentapi.Client(
            host=f"localhost:{self._port_WebUI}",
            username=self._user_WebUI,
            password=self._pass_WebUI
        )
        qbt_client.torrents_delete(
            torrent_hashes=self.torrent_hash,
            delete_files=False
        )
        time.sleep(1)

        if not self.is_folder:
            old_file = Path(self.qb_download_path)
            old_file.rename(Path(self.download_folder) / self.new_name)

        else:
            old_folder = Path(self.qb_download_path)

            for n, episode in enumerate(old_folder.iterdir(), start=1):
                new_name = f'{self.parent} - {str(n).zfill(2)}{episode.suffix}'
                episode.rename(old_folder / new_name)

            old_folder.rename(self.download_folder)

    def save_history(self):
        pass

    def log_error(self, error):
        pass


class AiringAnime:

    def __init__(self, **kwargs) -> None:
        self.title: str = kwargs['title']
        self.mal_id: str = kwargs['mal_id']
        self.score: float = kwargs['score']
        self.url: str = kwargs['url']
        self.episodes: int = kwargs['episodes']
        self.__set_schedule(kwargs['airing_start'])

    def __set_schedule(self, time_str: str):
        a = re.findall("(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", time_str)[0]
        a = [int(x) for x in a]
        self.airing_day: int = datetime(*a[:3]).weekday()
        self.airing_time: str = (
            datetime(*a) + timedelta(hours=3)).strftime('%H:%M')

    def __repr__(self) -> str:
        return f'{self.title}: {self.score}\n{self.airing_time}'
