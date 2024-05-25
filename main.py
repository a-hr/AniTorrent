import logging
from typing import List

import asyncio
import yaml
import qdarktheme
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QLineEdit, QHeaderView
from PyQt5.QtCore import QModelIndex, QThread

from WebAPI import Nyaa
from TorrentHandler import TorrentHandler, Torrent
from UI import MainWindow
from Models import SearchTableModel, EpisodeTableModel, FilterProxyModel
from Workers import DownloadWorker


class Config:
    def __init__(self):
        self.__load_config()

    def __load_config(self):
        with open("config.yaml") as file:
            self.__config = yaml.safe_load(file)

    def __save_config(self):
        with open("config.yaml", "w") as file:
            yaml.dump(self.__config, file)

    def __getitem__(self, key: str):
        return self.__config[key]

    def __setitem__(self, key: str, value):
        self.__config[key] = value
        self.__save_config()

    @property
    def config(self):
        return self.__config


class App(MainWindow):

    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.nyaa = Nyaa()
        self.handler = TorrentHandler(self.config.config)

        #! save .torrents.pkl file if closed during download, holding the torrent objects
        self.download_worker = DownloadWorker(self.handler)
        self.download_worker.update_signal.connect(
            self.downloads_widget.update_progress
        )
        self.download_worker.finished_signal.connect(
            lambda ts: self.downloads_completed(ts)
        )
        self.download_worker.start()

        # configure connections
        self.button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.button3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.button4.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        self.search_widget.search_bar.returnPressed.connect(
            lambda: self.search(self.search_widget.search_bar.text())
        )
        self.search_widget.search_button.clicked.connect(
            lambda: self.search(self.search_widget.search_bar.text())
        )

        self.search_widget.table_view.clicked.connect(self.update_results_table)

        self.results_widget.button_filter.clicked.connect(
            lambda: self.filter_results(False)
        )
        self.results_widget.button_reset.clicked.connect(
            lambda: self.filter_results(True)
        )
        self.results_widget.button_download.clicked.connect(self.download)

        self.settings_window.save_setts_button.clicked.connect(self.save_settings)
        self.settings_window.cancel_setts_button.clicked.connect(self.cancel_settings)

    def search(self, term: str):
        fansub = "subsplease"
        language = "english"

        loop = asyncio.get_event_loop()
        torrents = loop.run_until_complete(self.nyaa.search(term, fansub, language))

        if not torrents:
            self.info_box("No torrents found", f"No torrents found for '{term}'.")
            return

        series = list(
            set([torrent.series for torrent in torrents if torrent is not None])
        )
        self.update_search_table(series, fansub, language)

    def update_search_table(self, results: List[str], fansub: str, language: str):
        self.model_search = SearchTableModel(results, fansub, language)
        self.search_widget.table_view.setModel(self.model_search)
        self.search_widget.table_view.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )

    def update_results_table(self, selected: QModelIndex):
        self.stacked_widget.setCurrentIndex(1)
        series = self.model_search.return_selected(selected)

        loop = asyncio.get_event_loop()
        torrents = loop.run_until_complete(
            self.nyaa.search(series, "subsplease", "english")
        )
        torrents = [torrent for torrent in torrents if torrent is not None]

        if not torrents:
            self.info_box("No torrents found", f"No torrents found for this series.")
            return

        self.episodes_model = EpisodeTableModel(torrents)
        self.episodes_proxymodel = FilterProxyModel()
        self.episodes_proxymodel.setSourceModel(self.episodes_model)
        self.results_widget.table_view.setModel(self.episodes_proxymodel)

        self.results_widget.table_view.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )

    def filter_results(self, reset: bool):
        self.episodes_proxymodel.clearFilters()
        self.episodes_model.refresh()

        if reset:
            self.results_widget.combo_box.setCurrentIndex(0)
            self.results_widget.checkBox_batch.setChecked(False)
            return

        quality = self.results_widget.combo_box.currentText()
        filter_quality = quality if quality != "Select" else ""
        filter_batch = "true" if self.results_widget.checkBox_batch.isChecked() else ""

        if filter_quality:
            self.episodes_proxymodel.setFilterByColumn(2, filter_quality)
        if filter_batch:
            self.episodes_proxymodel.setFilterByColumn(3, filter_batch)

    def download(self, _: QModelIndex):
        self.stacked_widget.setCurrentIndex(2)
        torrents: list[Torrent] = self.episodes_model.return_selected()
        for torrent in torrents:
            self.handler.add_torrent(torrent)

    def downloads_completed(self, torrents: List[Torrent]):
        if not torrents:
            return

        for torrent in torrents:
            torrent.process()

        self.info_box(
            "Downloads Completed",
            "\n".join(
                [
                    f"Downloaded \n{torrent.series} - {torrent.episode}"
                    for torrent in torrents
                ]
            ),
        )

    def save_settings(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Confirm Action")
        dialog.setText("Are you sure you want to save?")
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)

        if dialog.exec_() == QMessageBox.Yes:
            # iterate through all widgets in settings window
            for widget in self.settings_window.findChildren(QWidget):
                # if widget is a line edit
                if isinstance(widget, QLineEdit):
                    key = widget.objectName().replace("line_", "")
                    value = widget.text()
                    self.settings[key] = value
            return

        # reset all line edits
        self.cancel_settings()

    def cancel_settings(self):
        # reset all line edits
        for widget in self.settings_window.findChildren(QWidget):
            if isinstance(widget, QLineEdit):
                key = widget.objectName().replace("line_", "")
                value = self.settings[key]
                widget.setText(value)

    def info_box(self, title, message):
        qm = QMessageBox()
        qm.information(self, title, message)

    def onClose(self):
        # self.handler.save_torrents()
        self.download_worker.stop()
        super().close()


if __name__ == "__main__":
    config = Config()

    with open("UI/qss.style") as file:
        qss = file.read()

    qdarktheme.enable_hi_dpi()

    app = QApplication([])
    qdarktheme.setup_theme("light", additional_qss=qss)

    window = App(config)
    window.show()

    app.exec_()
