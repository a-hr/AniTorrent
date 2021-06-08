import qbittorrentapi

from PyQt5 import QtCore

from tools import Engine
from .workers import Worker, ProgressObserver
from models import Episode, Torrent


class Functions(QtCore.QObject):

    send_torrents = QtCore.pyqtSignal(list)

    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent
        self.post_processing = 0

    def search(self) -> list[str]:

        SearchEngine = Engine(self.parent.current_fansub)
        search_term = self.parent.line_search.text()

        search_results = [serie for serie in SearchEngine.available_series() if SearchEngine.match(search_term, serie)]

        if search_results:
            return [serie_dict for serie_dict in search_results]
        
        else:
            return [f"No results for '{search_term}'.",]

    def episodes(self, QModelIndex = None, selected_series:str = None) -> list[Episode]:
        
        if QModelIndex:
            selected_series = self.parent.listWidget_search.itemFromIndex(QModelIndex).text()
    
        SearchEngine = Engine(self.parent.current_fansub)

        episodes_dicts = SearchEngine.search_episodes(selected_series)

        cleaned_results = episodes_dicts # self.clean_duplicates(episodes_dicts)

        if len(cleaned_results) == 0:
            return 'No results, found. Episodes not yet available.'

        else:
            return cleaned_results

    def download(self, torrents:list[Torrent]) -> list[Torrent]:
        
        qbt_client = qbittorrentapi.Client(
            host=f"localhost:{self.parent.config.port_WebUI}",
            username=self.parent.config.user_WebUI,
            password=self.parent.config.pass_WebUI,
            SIMPLE_RESPONSES=True
        )
        
        # Check if WebUI is up
        try:
            qbt_client.app_version()
        except:
            import os
            os.system(f'cmd /c "start /min "" "{self.parent.config.qbittorrent_path}""')
            
        for torrent in torrents:
            
            qbt_client.torrents_add(
                urls=torrent.magnet,
                save_path=torrent.download_folder,
                tags=torrent.tag,
                category='anitorrent')
        
        for response in qbt_client.torrents_info(category='anitorrent'):
            for torrent in torrents:
                if response['tags'] == torrent.tag:
                    torrent.torrent_hash = response['hash']
        
        self.timer.start(1500)
        
        return torrents
        
    def start_observing(self) -> None:
        self.progressThread = ProgressObserver(self.parent.config)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progressThread.update_progress)
        
        self.thread = QtCore.QThread()
        self.progressThread.moveToThread(self.thread)

        self.progressThread.update.connect(self.progress_update_handler)
        self.progressThread.torrent_completed.connect(self.finished_download_handler)
        self.progressThread.torrent_canceled.connect(self.canceled_download_handler)
        self.progressThread.finished.connect(self.endTimer)

        self.send_torrents.connect(self.progressThread.startTimer)

        self.thread.start()

    def endTimer(self) -> None:
        self.timer.stop()
        self.parent.download_table_refresh([])

    # <Slots>
    @QtCore.pyqtSlot(list)
    def progress_update_handler(self, torrents:list[Torrent]) -> None:
        self.parent.download_table_refresh(torrents)
            
    @QtCore.pyqtSlot(object)
    def finished_download_handler(self, torrent:Torrent) -> None:
        self.post_processing += 1
        worker = Worker(torrent.rename, torrent)
        worker.signals.finished.connect(self.rename_completed)
        worker.signals.error.connect(
            lambda error_t: self.parent.info_box('Error', str(error_t[-1])))
        self.parent.threadpool.start(worker)

    @QtCore.pyqtSlot(object)
    def canceled_download_handler(self, torrent:Torrent):
        self.parent.info_box(
            'Download canceled', f'{torrent.title} was canceled!')

    @QtCore.pyqtSlot(object)
    def rename_completed(self, torrent:Torrent):
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
