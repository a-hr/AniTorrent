import pickle
import sys
from pathlib import Path

import psutil
from PyQt5 import QtCore, QtGui, QtWidgets

from data import Config
from models import EpisodeTableModel, FilterProxyModel, SearchTableModel
from tools import Functions
from ui import GUI, AiringToday, ScheduleWindow


class MainWindow(GUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.functions = Functions(self)
        self.setup()
        self.label_user_icon.setText("アニメ")
        self.label_user_icon.setFont(QtGui.QFont("Segoe UI", 17))
        self.label_top_info_1.setFont(QtGui.QFont("Segoe UI", 10, 6))

        if not Path(f"{self.config.download_path}").exists():
            self.stackedWidget.setCurrentIndex(3)
            warning = f"""The provided download path ({
                self.config.download_path}) does not exist. Please select a new one."""
            self.info_box("Warning", warning)

        if (bf := self.config.backup_file).exists():
            with open(bf, "rb") as f:
                if running_torrents := pickle.load(f):
                    self.functions.send_torrents.emit(running_torrents)
            bf.unlink()

    def setup(self):
        # <Setup>
        self.ui_init()

        self.current_fansub = str()
        self.selected_fansubs = list()

        self.config = Config()
        self.threadpool = QtCore.QThreadPool()

        self.functions.start_observing()

        if not "qbittorrent.exe" in (p.name() for p in psutil.process_iter()):
            import os

            os.system(f'cmd /c "start /min "" "{self.config.qbittorrent_path}""')

        # <Connections>
        self.button_airingtoday.clicked.connect(self.airingToday)
        self.button_schedule.clicked.connect(self.schedule)

        self.line_search.returnPressed.connect(self.search)
        self.button_search.clicked.connect(self.search)

        self.tableView_search.clicked.connect(lambda parent: self.load_childs(parent))

        self.pushButton_filter.clicked.connect(lambda: self.filter_results(reset=False))
        self.pushButton_resetfilter.clicked.connect(
            lambda: self.filter_results(reset=True)
        )

        self.pushButton_download.clicked.connect(self.download)

        self.pushButton_change_settings.clicked.connect(self.save_settings_reload)
        self.pushButton_download_path.clicked.connect(
            lambda: self.select_file_dir(select="download_dir")
        )
        self.pushButton_qB_path.clicked.connect(
            lambda: self.select_file_dir(select="qbt_path")
        )

    # <Helpers>
    def info_box(self, title, message):
        qm = QtWidgets.QMessageBox()
        qm.information(self, title, message)

    def download_table_refresh(self, torrents: list):

        self.tableWidget_downloads.clearContents()
        self.tableWidget_downloads.setRowCount(len(torrents))

        for row, torrent in enumerate(torrents):

            title = QtWidgets.QTableWidgetItem(torrent.title)

            pb = QtWidgets.QProgressBar()
            pb.setValue(torrent.progress)
            pb.setStyleSheet(
                """
                QProgressBar {
                    background-color: rgb(52, 59, 72);
                    border-radius: 1px;
                    text-align: center;
                }
                            
                QProgressBar::chunk {
                    background-color: rgb(85, 170, 255);
                    border-radius: 1px;
                } """
            )

            eta = QtWidgets.QTableWidgetItem(
                f"{int(torrent.eta/60)}m" if torrent.eta > 60 else f"{torrent.eta}s"
            )

            self.tableWidget_downloads.setItem(row, 0, title)
            self.tableWidget_downloads.setCellWidget(row, 1, pb)
            self.tableWidget_downloads.setItem(row, 2, eta)

    def save_settings(self):

        reply = QtWidgets.QMessageBox.question(
            self,
            "Change settings",
            """Settings will be saved and app reloaded.
                \nAre you sure you want to proceed?""",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )

        if reply == QtWidgets.QMessageBox.Yes:

            val_folders = (
                self.lineEdit_qB_path.text(),
                self.lineEdit_download_path.text(),
            )

            val_settings = (
                not self.checkBox_cancel_postprocessing.isChecked(),
                self.checkBox_custom_WebUi.isChecked(),
                self.lineEdit_WebUi_user.text(),
                self.lineEdit_WebUi_pass.text(),
                self.lineEdit_WebUi_port.text(),
            )

            self.config.save_changes(val_folders=val_folders, val_settings=val_settings)

            self.info_box("Completed", "Settings were updated.")

        else:
            self.info_box("Canceled", "No changes were made.")

    # <Main Methods>
    @QtCore.pyqtSlot()
    def search(self) -> None:
        self.selected_fansubs = self.combobox_fansubs.returnChecked()

        results = self.functions.search()

        if isinstance(results, dict):
            self.model_search = SearchTableModel(results)
            self.tableView_search.setModel(self.model_search)
            self.tableView_search.resizeColumnsToContents()
        else:
            self.info_box("Empty query", results)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def load_childs(self, parent) -> None:

        result = self.functions.episodes(QModelIndex=parent)
        if isinstance(result, list):
            self.episodes_model = EpisodeTableModel(result, self.config)
            self.episodes_proxymodel = FilterProxyModel()
            self.episodes_proxymodel.setSourceModel(self.episodes_model)
            self.tableView_episodes.setModel(self.episodes_proxymodel)

            header = self.tableView_episodes.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

            self.stackedWidget.setCurrentIndex(1)
            self.swapMenus("btn_results")
        else:
            self.info_box("Empty query", result)

    @QtCore.pyqtSlot(bool)
    def download(self, *args) -> None:

        torrent_list = self.episodes_model.returnSelected()  # raw
        self.episodes_model.refresh()

        torrent_list = self.functions.download(torrent_list)  # hash + qb_path
        self.functions.send_torrents.emit(torrent_list)

        if torrent_list:
            self.stackedWidget.setCurrentIndex(2)
            self.swapMenus("btn_downloads")

    # <Slots>
    @QtCore.pyqtSlot()
    def select_file_dir(self, select: str) -> None:

        if select == "download_dir":
            dir = QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select folder", options=QtWidgets.QFileDialog.ShowDirsOnly
            )

            self.lineEdit_download_path.setText(dir)

        elif select == "qbt_path":
            file = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select file", "C:\Program Files\qBittorrent"
            )

            self.lineEdit_qB_path.setText(file[0])

    @QtCore.pyqtSlot(bool)
    def filter_results(self, reset):

        self.episodes_proxymodel.clearFilters()

        if not reset:
            filter_quality = (
                self.comboBox_quality.currentText()
                if self.comboBox_quality.currentIndex() > 0
                else ""
            )
            filter_batch = "True" if self.checkBox_batch.isChecked() else ""

            self.episodes_proxymodel.setFilterByColumn(1, filter_quality)
            self.episodes_proxymodel.setFilterByColumn(2, filter_batch)

    @QtCore.pyqtSlot()
    def airingToday(self):
        self.airingTodayWindow = AiringToday(self.config)
        self.airingTodayWindow.show()
        self.airingTodayWindow.search_title.connect(
            lambda text: self.line_search.setText(text)
        )

    @QtCore.pyqtSlot()
    def schedule(self):
        self.scheduleWindow = ScheduleWindow(self.config)
        self.scheduleWindow.show()
        self.scheduleWindow.search_title.connect(
            lambda text: self.line_search.setText(text)
        )

    @QtCore.pyqtSlot()
    def save_settings_reload(self):
        self.save_settings()
        self.config = Config()
        self.setup_settings()

    def closeEvent(self, event):

        if self.functions.progressThread.running:
            torrent_list = self.functions.progressThread.torrents.copy()
            with open(self.config.backup_file, "wb") as f:
                pickle.dump(torrent_list, f)
        else:
            self.functions.thread.quit()

        if self.functions.post_processing:

            reply = QtWidgets.QMessageBox.question(
                self,
                "Quit",
                """A file is still being processed (<30s left)
                \nAre you sure you want to quit?""",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )

            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()


def launch():
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont("ui/fonts/segoeui.ttf")
    QtGui.QFontDatabase.addApplicationFont("ui/fonts/segoeuib.ttf")
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch()
