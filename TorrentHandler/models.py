from urllib.parse import urlparse, parse_qs
from pathlib import Path


class QBittorrentNotRunning(Exception):
    pass


class Torrent:
    def __init__(self, **kwargs):
        # Global attributes
        __atributes__ = ["raw_title", "series", "quality", "batch"]
        for attr in __atributes__:
            try:
                setattr(self, attr, kwargs[attr])
            except KeyError:
                raise KeyError(f"Missing required argument {attr}")

        self.magnet: str = ""
        self.hash: str = ""

        # Batch attributes
        if self.batch:
            self.episode_start: str = kwargs["episode_start"]
            self.episode_end: str = kwargs["episode_end"]

        # Episode attributes
        else:
            self.episode: str = kwargs["episode"]

        # Flags
        self.eta: int = 0
        self.progress: int = 0
        self.downloaded: bool = False
        self.processed: bool = False  # True if processed after download
        self.download_path: str = ""

    def add_magnet(self, magnet: str) -> None:
        self.magnet = magnet
        self.hash = parse_qs(urlparse(self.magnet).query)["xt"][0].split(":")[-1]

    def update_progress(self, query_data: dict) -> object:
        self.progress = int(query_data["progress"] * 100)

        if self.progress == 100:
            self.downloaded = True
            return self
        
        self.eta = query_data["eta"]
        self.download_path = query_data["content_path"]
        # self.root_path = query_data["root_path"]
        return self

    def process(self) -> None:
        """
        Torrents ready to process are retrieved from TorrentHandler.update_status().
        They are already removed from the client and safe to process.
        """
        self.processed = True

        if not self.batch:
            # create a new path for the episode
            new_path = Path(self.download_path).with_stem(f"{self.series} - {self.episode}")
            Path(self.download_path).rename(new_path)
            return

        old_folder = Path(self.download_path)
        for n, episode in enumerate(old_folder.iterdir(), start=1):
            new_name = f"{self.series} - {str(n).zfill(2)}"
            episode.rename(episode.with_stem(new_name))
        
        old_folder.rename(old_folder.with_stem(self.series))

    def __repr__(self) -> str:
        r = f"{self.series} - "
        r += f"{self.episode if not self.batch else self.episode_start + '-' + self.episode_end}"
        r += f" ({self.quality})"
        return r
