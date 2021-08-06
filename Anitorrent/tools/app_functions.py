import time

import qbittorrentapi
from models import Episode, Torrent
from PyQt5 import QtCore

from tools import PluginEngine

from .workers import ProgressObserver, Worker


class Functions(QtCore.QObject):

    send_torrents = QtCore.pyqtSignal(list)

    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent
        self.post_processing = 0

    def search(self) -> dict:
        SearchEngine = PluginEngine(self.parent.selected_fansubs)
        search_term = self.parent.line_search.text()
        search_results = SearchEngine.available_series(search_term)
        not_empty = [True for res in search_results.values() if res]
        return search_results if not_empty else f"No results for '{search_term}'."

    def episodes(self, QModelIndex=None, table_response: list = None) -> list[Episode]:
        if QModelIndex:
            selected_series, fansub = self.parent.model_search.return_selected(
                QModelIndex)
        else:
            selected_series, fansub = table_response
        
        self.parent.current_fansub = fansub
        SearchEngine = PluginEngine()
        episodes_dicts = SearchEngine.search_episodes(fansub, selected_series)

        # self.clean_duplicates(episodes_dicts)
        cleaned_results = episodes_dicts

        if len(cleaned_results) == 0:
            return 'No results found. Episodes not yet available.'

        else:
            return cleaned_results

    def download(self, torrents: list[Torrent]) -> list[Torrent]:

        # Check if WebUI is up
        try:
            client = qbittorrentapi.Client(
                host=f"localhost:{self.parent.config.port_WebUI}",
                username=self.parent.config.user_WebUI,
                password=self.parent.config.pass_WebUI)
            client.app_version()
        except:
            import os
            os.system(
                f'cmd /c "start /min "" "{self.parent.config.qbittorrent_path}""')
        finally:
            qbt_client = qbittorrentapi.Client(
                host=f"localhost:{self.parent.config.port_WebUI}",
                username=self.parent.config.user_WebUI,
                password=self.parent.config.pass_WebUI,
                SIMPLE_RESPONSES=True)

        for torrent in torrents:

            qbt_client.torrents_add(
                urls=torrent.magnet,
                save_path=torrent.download_folder,
                tags=torrent.tag,
                category='anitorrent')

        paired_torrents = []
        while torrents:
            qb_torrents = qbt_client.torrents_info(category='anitorrent')
            for torrent in torrents:
                for response in qb_torrents:
                    if response['tags'] == torrent.tag:
                        torrent.torrent_hash = response['hash']
                        paired_torrents.append(torrent)
                        torrents.remove(torrent)
        
        if not self.timer.isActive():
            self.timer.start(1500)

        return paired_torrents

    def start_observing(self) -> None:
        self.progressThread = ProgressObserver(self.parent.config)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progressThread.update_progress)
        self.timer.start(1500)

        self.thread = QtCore.QThread()
        self.progressThread.moveToThread(self.thread)

        self.progressThread.update.connect(self.progress_update_handler)
        self.progressThread.torrent_completed.connect(
            self.finished_download_handler)
        self.progressThread.torrent_canceled.connect(
            self.canceled_download_handler)
        self.progressThread.finished.connect(self.endTimer)

        self.send_torrents.connect(self.progressThread.startTimer)

        self.thread.start()

    def endTimer(self) -> None:
        self.timer.stop()
        self.parent.download_table_refresh([])

    # <Slots>
    @QtCore.pyqtSlot(list)
    def progress_update_handler(self, torrents: list[Torrent]) -> None:
        self.parent.download_table_refresh(torrents)

    @QtCore.pyqtSlot(object)
    def finished_download_handler(self, torrent: Torrent) -> None:
        self.post_processing += 1
        worker = Worker(torrent.rename, torrent)
        worker.signals.finished.connect(self.rename_completed)
        worker.signals.error.connect(
            lambda error_t: self.parent.info_box('Error', str(error_t[-1])))
        self.parent.threadpool.start(worker)

    @QtCore.pyqtSlot(object)
    def canceled_download_handler(self, torrent: Torrent):
        self.parent.info_box(
            'Download canceled', f'{torrent.title} was canceled!')

    @QtCore.pyqtSlot(object)
    def rename_completed(self, torrent: Torrent):
        self.post_processing -= 1
        self.parent.info_box(
            'Completed', f'{torrent.title} was correctly downloaded!')

    # </Slots>
    @staticmethod
    def clean_duplicates(results: list[dict]) -> list[dict]:

        clean_results = []

        length = len(results)

        if length == 1:
            clean_results = results

        elif length > 1:

            for index in range(length - 1):

                if results[index]['title'] != results[index + 1]['title'] or results[index]['quality'] != results[index + 1]['quality']:

                    clean_results.append(results[index])

            clean_results.append(results[-1])

        return clean_results
