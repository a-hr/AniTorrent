from  pathlib import Path
import time
import qbittorrentapi
from random import randint


class Episode:
    
    __slots__ = (
        'title', 'suffix', 'series_name', 'quality', 'episode_str', 'episode_int', 'batch', 'magnet'
        )

    def __init__(
        self,
        magnet_link,
        **kwargs
        ) -> None:
        
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.magnet = magnet_link


class Torrent:
    
    def __init__(self,
                 episode_obj: Episode,
                 config_object
                 ) -> None:
        
        self.__config = config_object
        
        self.status = ''
        self.progress = 0
        self.eta = 0
        
        self.torrent_hash = ''
        self.magnet = episode_obj.magnet

        self.postprocess = self.__config.postprocess
        
        self.new_name = f'{episode_obj.title}{episode_obj.suffix}'
        self.parent = episode_obj.series_name
        self.qb_download_path = ''

        self.title = episode_obj.title
        self.is_folder = episode_obj.batch

        if self.is_folder:
            self.download_folder = self.__config.download_path
        else:
            self.download_folder = f'{self.__config.download_path}/{self.parent}'

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
            host=f"localhost:{self.__config.port_WebUI}",
            username=self.__config.user_WebUI,
            password=self.__config.pass_WebUI
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

