import time
from typing import Dict, List, Tuple, TypeVar
from subprocess import Popen
from pathlib import Path

import requests
from qbittorrentapi import Client

from .models import Torrent, QBittorrentNotRunning


MAX_RETRIES = 5


def check_connection(host: str) -> bool:
    try:
        _ = requests.get(host, timeout=1)
    except requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout:
        return False
    return True


def launch_client(qbittorrent_path: str) -> None:
    # launch qbittorrent, taking into account the OS
    if qbittorrent_path.endswith(".exe"):
        Popen(qbittorrent_path)
    elif qbittorrent_path.endswith(".app"):
        Popen(["open", qbittorrent_path])
    elif qbittorrent_path.endswith(".sh"):
        Popen(["sh", qbittorrent_path])
    return


class TorrentHandler:
    def __init__(self, config: dict):
        self.root_path = config["download_path"]
        self.client = self.__init_client(
            config["user"],
            config["password"],
            config["host"],
            config["qbittorrent_path"],
        )

        self.torrents: Dict[str, Torrent] = {}  # hash: Torrent
        self.ended_torrents: Dict[float, Torrent] = {}  # started_time: Torrent

    def add_torrent(self, torrent: Torrent):
        if torrent.hash in self.torrents:
            return

        self.torrents[torrent.hash] = torrent

        save_path = Path(self.root_path) / torrent.series
        save_path.mkdir(parents=True, exist_ok=True)

        self.client.torrents_add(urls=torrent.magnet, save_path=save_path)

    def manual_remove(self, torrent: Torrent):
        self.client.torrents_delete(hashes=torrent.hash, delete_files=True)
        try:
            del self.torrents[torrent.hash]
        except KeyError:
            pass

    def update(self) -> Tuple[List[Torrent], List[Torrent]]:
        """Updates the status of all active torrents and returns a list of torrents to show and to notify that were downloaded.

        Returns:
            Tuple[List[Torrent], List[Torrent]]: a list of torrents that can be processed.
        """
        _to_remove = []

        for _hash, torrent in self.torrents.items():
            # update progress status
            response = self.client.torrents_info(hashes=_hash)

            # if the hash is not in the response, the torrent has been removed
            if not response:
                # mark the hash for removal
                _to_remove.append(_hash)
                continue

            # if the torrent has finished downloading, mark it for processing
            if torrent.downloaded:
                self.ended_torrents[time.time()] = torrent
                _to_remove.append(_hash)
                continue

        # remove marked torrents from active torrents
        for _hash in _to_remove:
            del self.torrents[_hash]

        # check if resting torrents are ready to be processed
        _to_remove = []
        _to_process = []
        for started_time, torrent in self.ended_torrents.items():
            if self.__check_rested(started_time):
                _to_process.append(torrent)
                _to_remove.append(started_time)

        # remove processed torrents from client
        if _to_process:
            self.client.torrents_delete(
                hashes=[torrent.hash for torrent in _to_process], delete_files=False
            )

        # remove processed torrents from ended torrents
        for started_time in _to_remove:
            del self.ended_torrents[started_time]

        return self._get_progress(), _to_process

    def _get_progress(self) -> List[Torrent]:
        """Get the status of all active (and resting) torrents, update their progress and return them.
        Returns:
            List[Torrent]: updated torrents
        """
        active_hashes = list(self.torrents.keys())
        response = self.client.torrents_info(torrent_hashes=active_hashes)

        r = [
            self.torrents[info["hash"]].update_progress(info)
            for info in response
            if info["hash"] in active_hashes
        ]
        r.extend(self.ended_torrents.values())
        return r

    def __init_client(self, user: str, pwd: str, host: str, qbt_path: str) -> Client:
        # check if qbittorrent is running
        retries = 0
        while not check_connection(host):
            launch_client(qbt_path)
            time.sleep(1)
            retries += 1
            if retries == MAX_RETRIES:
                raise QBittorrentNotRunning(
                    f"qBittorrent is not running, is the path {qbt_path} correct?"
                )

        return Client(host=host, username=user, password=pwd)

    def __check_rested(self, started: float) -> bool:
        """Check if the torrent has been 'resting' for at least 30 seconds to ensure it isn't corrupted.

        Args:
            started (float): the time the torrent was marked as 'downloaded'

        Returns:
            bool: true if the torrent is ready to be processed.
        """
        return (time.time() - started) > 30
