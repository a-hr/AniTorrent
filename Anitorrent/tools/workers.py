import sys
import traceback
import time
import qbittorrentapi

from PyQt5 import QtCore
from models import Torrent


class ProgressObserver(QtCore.QObject):

    update = QtCore.pyqtSignal(list)
    torrent_completed = QtCore.pyqtSignal(object)
    torrent_canceled = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception)
    finished = QtCore.pyqtSignal()

    def __init__(self,  config) -> None:
        super().__init__()

        self.config = config
        
        self.running = False
        self.torrents = []

        self.qbt_client = qbittorrentapi.Client(
            host=f"localhost:{self.config.port_WebUI}",
            username=self.config.user_WebUI,
            password=self.config.pass_WebUI)

    def update_progress(self):

        for torrent in self.torrents:

            response = self.qbt_client.torrents_info(
                torrent_hash=torrent.torrent_hash,
                SIMPLE_RESPONSES=True)
            
            datas = [data for data in response 
            if data['hash'] == torrent.torrent_hash]

            if not datas:
                self.torrent_canceled.emit(torrent)
                self.torrents.remove(torrent)

            elif torrent.update_progress(datas[0]):
                self.torrent_completed.emit(torrent)
                self.torrents.remove(torrent)

        if self.torrents:
            self.update.emit(self.torrents)

        else:
            self.finished.emit()
            self.running = False
            self.torrents = []

    @QtCore.pyqtSlot(list)
    def startTimer(self, torrents:list[Torrent]):

        if not self.running:
            self.running = True
            self.torrents = [torrent for torrent in torrents]
        
        else:
            [self.torrents.append(torrent)for torrent in torrents 
            if torrent not in self.torrents]


class ProcessSignals(QtCore.QObject):

    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(tuple)


class Worker(QtCore.QRunnable):

    def __init__(self, fn, torrent_obj):
        super(Worker, self).__init__()
        self.fn = fn
        self.torrent_obj = torrent_obj
        self.signals = ProcessSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            time.sleep(30)
            self.fn()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit(self.torrent_obj)