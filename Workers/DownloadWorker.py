from PyQt5.QtCore import QThread, pyqtSignal, QTimer

from TorrentHandler import TorrentHandler


class DownloadWorker(QThread):
    update_signal = pyqtSignal(list)
    finished_signal = pyqtSignal(list)

    def __init__(self, torrent_handler):
        super().__init__()
        self.torrent_handler: TorrentHandler = torrent_handler
        self.timer = None
        # TODO: load torrents from file (if unexpected shutdown)

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_torrents)
        self.timer.start(1000)
        self.exec_()  # Start the event loop

    def update_torrents(self):
        active_downloads, finished = self.torrent_handler.update()
        self.update_signal.emit(active_downloads)
        self.finished_signal.emit(finished)

    def stop(self):
        if self.timer:
            self.timer.stop()
        self.quit()
        self.wait()
