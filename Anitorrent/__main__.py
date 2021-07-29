import ctypes
import sys
from pathlib import Path

import psutil
from PyQt5 import QtCore, QtGui, QtWidgets

from data import Config
from models import (AiringAnime, EpisodeTableModel, FilterProxyModel,
                    ScheduleTableModel, SearchTableModel)
from tools import Functions, PluginEngine
from ui import CheckableComboBox, Ui_AiringToday, Ui_MainWindow, Ui_Schedule


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        self.functions = Functions(self)

        self.setup()
        self.setup_menus()
        self.setup_settings()
        self.uiDefinitions()

        self.show()

        if not Path(f'{self.config.download_path}').exists():
            self.stackedWidget.setCurrentIndex(3)
            warning = "The provided download path does not exist. Please select a new one."
            self.info_box('Warning', warning)

    def setup(self):

        # <Setup>
        self.clicked = False
        self.current_fansub = str()
        self.selected_fansubs = list()

        self.config = Config()
        self.setWindowIcon(QtGui.QIcon(self.config.icon))
        myappid = u'Kajiya_aru.AniTorrent.v1_0_0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.threadpool = QtCore.QThreadPool()

        self.functions.start_observing()

        if not "qbittorrent.exe" in (p.name() for p in psutil.process_iter()):
            import os
            os.system(
                f'cmd /c "start /min "" "{self.config.qbittorrent_path}""')
        # </Setup>

        # <GUI Properties>
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowTitle('AniTorrent')

        startSize = QtCore.QSize(1000, 720)
        self.setFixedSize(startSize)

        self.label_title_bar_top.setText('AniTorrent')
        self.label_credits.setText('Developed by: Kajiya_aru')
        self.label_version.setText('v1.0.0')
        # </GUI Properties>

        # <Widget Properties>
        self.combobox_fansubs = CheckableComboBox()
        for index, fansub in enumerate(self.config.plugins):
            self.combobox_fansubs.addItem(fansub[0])
            self.combobox_fansubs.setItemChecked(index, checked=fansub[1])

        self.verticalLayout_10.replaceWidget(
            self.combobox_source, self.combobox_fansubs)
        self.combobox_source.close()

        self.tableView_search.verticalHeader().setVisible(False)
        self.tableView_episodes.verticalHeader().setVisible(False)
        self.tableWidget_downloads.verticalHeader().setVisible(False)

        self.tableWidget_downloads.setColumnCount(3)
        self.tableWidget_downloads.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_downloads.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignCenter)
        self.tableWidget_downloads.setHorizontalHeaderLabels((
            "Name", "Progress", "Remaining"))

        header = self.tableWidget_downloads.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        # </Widget Properties>

        # <Connections>
        self.button_airingtoday.clicked.connect(self.airingToday)
        self.button_schedule.clicked.connect(self.schedule)

        self.line_search.returnPressed.connect(self.search)
        self.button_search.clicked.connect(self.search)

        self.tableView_search.clicked.connect(
            lambda parent: self.load_childs(parent))

        self.pushButton_filter.clicked.connect(
            lambda: self.filter_results(reset=False))
        self.pushButton_resetfilter.clicked.connect(
            lambda: self.filter_results(reset=True))

        self.pushButton_download.clicked.connect(self.download)

        self.pushButton_change_settings.clicked.connect(
            self.save_settings_reload)
        self.pushButton_download_path.clicked.connect(
            lambda: self.select_file_dir(select='download_dir'))
        self.pushButton_qB_path.clicked.connect(
            lambda: self.select_file_dir(select='qbt_path'))
        # </Connections>

    # <UI Management>
    def setup_menus(self):

        self.btn_toggle_menu.clicked.connect(
            lambda: self.toggleMenu(220, True))

        self.stackedWidget.setMinimumWidth(20)
        self.addNewMenu(
            "Search",
            "btn_search",
            "url(:/16x16/icons/16x16/cil-magnifying-glass.png)", True)
        self.addNewMenu(
            "Results", "btn_results",
            "url(:/16x16/icons/16x16/cil-browser.png)", True)
        self.addNewMenu(
            "Downloads",
            "btn_downloads",
            "url(:/16x16/icons/16x16/cil-data-transfer-down.png)", True)
        self.addNewMenu(
            "Settings",
            "btn_settings",
            "url(:/16x16/icons/16x16/cil-settings.png)", False)
        self.addNewMenu(
            "About",
            "btn_about",
            "url(:/16x16/icons/16x16/cil-people.png)", False)

        self.selectStandardMenu("btn_search")
        self.stackedWidget.setCurrentWidget(self.page_home)
        self.labelPage('SEARCH')

    def setup_settings(self):

        self.lineEdit_qB_path.setText(self.config.qbittorrent_path)
        self.lineEdit_download_path.setText(self.config.download_path)

        self.checkBox_cancel_postprocessing.setCheckState(
            QtCore.Qt.Unchecked if self.config.postprocess else QtCore.Qt.Checked)

        self.checkBox_custom_WebUi.setCheckState(
            QtCore.Qt.Checked if self.config.custom_WebUI else QtCore.Qt.Unchecked)
        self.checkBox_custom_WebUi.stateChanged.connect(
            lambda: self.toggleWebUIState(self.checkBox_custom_WebUi.isChecked()))

        self.lineEdit_WebUi_user.setText(self.config.user_WebUI)
        self.lineEdit_WebUi_pass.setText(self.config.pass_WebUI)
        self.lineEdit_WebUi_port.setText(str(self.config.port_WebUI))
        self.toggleWebUIState(self.checkBox_custom_WebUi.isChecked())

        self.lineEdit_username.setText(self.config.user_label)
        self.label_user_icon.setText(self.config.user_label)

    def uiDefinitions(self):

        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 150))
        self.frame_main.setGraphicsEffect(self.shadow)

        self.btn_minimize.clicked.connect(lambda: self.showMinimized())
        self.btn_close.clicked.connect(lambda: self.close())

    def addNewMenu(self, name, objName, icon, isTopMenu):

        style = """
            QPushButton {
                background-image: ICON_REPLACE;
                background-position: left center;
                background-repeat: no-repeat;
                border: none;
                border-left: 28px solid rgb(27, 29, 35);
                background-color: rgb(27, 29, 35);
                text-align: left;
                padding-left: 45px;
            }
            QPushButton[Active=true] {
                background-image: ICON_REPLACE;
                background-position: left center;
                background-repeat: no-repeat;
                border: none;
                border-left: 28px solid rgb(27, 29, 35);
                border-right: 5px solid rgb(44, 49, 60);
                background-color: rgb(27, 29, 35);
                text-align: left;
                padding-left: 45px;
            }
            QPushButton:hover {
                background-color: rgb(33, 37, 43);
                border-left: 28px solid rgb(33, 37, 43);
            }
            QPushButton:pressed {
                background-color: rgb(85, 170, 255);
                border-left: 28px solid rgb(85, 170, 255);
            }
        """
        font = QtGui.QFont()
        font.setFamily(u"Segoe UI")
        button = QtWidgets.QPushButton('1', self)
        button.setObjectName(objName)
        sizePolicy3 = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QtCore.QSize(0, 70))
        button.setLayoutDirection(QtCore.Qt.LeftToRight)
        button.setFont(font)
        button.setStyleSheet(style.replace('ICON_REPLACE', icon))
        button.setText(name)
        button.setToolTip(name)
        button.clicked.connect(self.Button)

        if isTopMenu:
            self.layout_menus.addWidget(button)
        else:
            self.layout_menu_bottom.addWidget(button)

    def toggleMenu(self, maxWidth, enable):
        if enable:
            width = self.frame_left_menu.width()
            maxExtend = maxWidth
            standard = 70

            if width == 70:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            self.animation = QtCore.QPropertyAnimation(
                self.frame_left_menu, b"minimumWidth")
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()

    # <Helpers>
    def toggleWebUIState(self, flag):
        self.lineEdit_WebUi_user.setEnabled(flag)
        self.lineEdit_WebUi_pass.setEnabled(flag)
        self.lineEdit_WebUi_port.setEnabled(flag)

    def selectStandardMenu(self, widget):
        for w in self.frame_left_menu.findChildren(QtWidgets.QPushButton):
            if w.objectName() == widget:
                w.setStyleSheet(self.selectMenu(w.styleSheet()))

    def resetStyle(self, widget):
        for w in self.frame_left_menu.findChildren(QtWidgets.QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(self.deselectMenu(w.styleSheet()))

    def swapMenus(self, widget):
        for w in self.frame_left_menu.findChildren(QtWidgets.QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(self.deselectMenu(w.styleSheet()))
            else:
                w.setStyleSheet(self.selectMenu(w.styleSheet()))

    def labelPage(self, text):
        newText = '| ' + text.upper()
        self.label_top_info_2.setText(newText)

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
                } """)

            eta = QtWidgets.QTableWidgetItem(
                f'{int(torrent.eta/60)}m' if torrent.eta > 60 else f'{torrent.eta}s')

            self.tableWidget_downloads.setItem(row, 0, title)
            self.tableWidget_downloads.setCellWidget(row, 1, pb)
            self.tableWidget_downloads.setItem(row, 2, eta)

    def save_settings(self):

        reply = QtWidgets.QMessageBox.question(
            self,
            'Change settings',
            """Settings will be saved and app reloaded.
                \nAre you sure you want to proceed?""",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:

            val_folders = (
                self.lineEdit_qB_path.text(),
                self.lineEdit_download_path.text())

            val_settings = (
                not self.checkBox_cancel_postprocessing.isChecked(),
                self.lineEdit_username.text(),
                self.checkBox_custom_WebUi.isChecked(),
                self.lineEdit_WebUi_user.text(),
                self.lineEdit_WebUi_pass.text(),
                self.lineEdit_WebUi_port.text())

            self.config.save_changes(
                val_folders=val_folders,
                val_settings=val_settings)

            self.info_box('Completed', 'Settings were updated.')

        else:
            self.info_box('Canceled', 'No changes were made.')

    @staticmethod
    def selectMenu(getStyle):
        select = getStyle + (
            "QPushButton { border-right: 7px solid rgb(44, 49, 60); }")
        return select

    @staticmethod
    def deselectMenu(getStyle):
        deselect = getStyle.replace(
            "QPushButton { border-right: 7px solid rgb(44, 49, 60); }", "")
        return deselect

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
            self.info_box('Empty query', results)

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
            header.setSectionResizeMode(
                3, QtWidgets.QHeaderView.ResizeToContents)

            self.stackedWidget.setCurrentIndex(1)
            self.swapMenus("btn_results")
        else:
            self.info_box('Empty query', result)

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

        if select == 'download_dir':
            dir = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                'Select folder',
                options=QtWidgets.QFileDialog.ShowDirsOnly)

            self.lineEdit_download_path.setText(dir)

        elif select == 'qbt_path':
            file = QtWidgets.QFileDialog.getOpenFileName(
                self,
                'Select file',
                'C:\Program Files\qBittorrent')

            self.lineEdit_qB_path.setText(file[0])

    @QtCore.pyqtSlot(bool)
    def filter_results(self, reset):

        self.episodes_proxymodel.clearFilters()

        if not reset:
            filter_quality = self.comboBox_quality.currentText(
            ) if self.comboBox_quality.currentIndex() > 0 else ''
            filter_batch = 'True' if self.checkBox_batch.isChecked() else ''

            self.episodes_proxymodel.setFilterByColumn(1, filter_quality)
            self.episodes_proxymodel.setFilterByColumn(2, filter_batch)

    @QtCore.pyqtSlot()
    def airingToday(self):
        self.airingTodayWindow = AiringToday()
        self.airingTodayWindow.show()
        self.airingTodayWindow.search_title.connect(
            lambda text: self.line_search.setText(text))

    @QtCore.pyqtSlot()
    def schedule(self):
        self.scheduleWindow = ScheduleWindow()
        self.scheduleWindow.show()
        self.scheduleWindow.search_title.connect(
            lambda text: self.line_search.setText(text))

    @QtCore.pyqtSlot()
    def save_settings_reload(self):
        self.save_settings()
        self.config = Config()
        self.setup_settings()

    @QtCore.pyqtSlot()
    def Button(self):
        btnWidget = self.sender()

        # PAGE HOME
        if btnWidget.objectName() == "btn_search":
            self.stackedWidget.setCurrentWidget(self.page_home)
            self.resetStyle("btn_search")
            self.labelPage("Search")
            btnWidget.setStyleSheet(self.selectMenu(btnWidget.styleSheet()))

        # PAGE RESULTS
        if btnWidget.objectName() == "btn_results":
            self.stackedWidget.setCurrentWidget(self.page_results)
            self.resetStyle("btn_results")
            self.labelPage("Results")
            btnWidget.setStyleSheet(self.selectMenu(btnWidget.styleSheet()))

        # PAGE DOWNLOADS
        if btnWidget.objectName() == "btn_downloads":
            self.stackedWidget.setCurrentWidget(self.page_downloads)
            self.resetStyle("btn_downloads")
            self.labelPage("Downloads")
            btnWidget.setStyleSheet(self.selectMenu(btnWidget.styleSheet()))

        # PAGE SETTINGS
        if btnWidget.objectName() == "btn_settings":
            self.stackedWidget.setCurrentWidget(self.page_widgets)
            self.resetStyle("btn_settings")
            self.labelPage("Custom Settings")
            btnWidget.setStyleSheet(self.selectMenu(btnWidget.styleSheet()))

        # PAGE ABOUT
        if btnWidget.objectName() == "btn_about":
            self.stackedWidget.setCurrentWidget(self.page_about)
            self.resetStyle("btn_about")
            self.labelPage("About")
            btnWidget.setStyleSheet(self.selectMenu(btnWidget.styleSheet()))

    # <App Events>
    def mousePressEvent(self, event):
        self.old_pos_x = int(event.screenPos().x())
        self.old_pos_y = int(event.screenPos().y())

    def mouseMoveEvent(self, event):
        if self.clicked:
            dx = self.old_pos_x - int(event.screenPos().x())
            dy = self.old_pos_y - int(event.screenPos().y())
            self.move(self.pos().x() - dx, self.pos().y() - dy)

        self.old_pos_x = int(event.screenPos().x())
        self.old_pos_y = int(event.screenPos().y())
        self.clicked = True

        return QtWidgets.QMainWindow.mouseMoveEvent(self, event)

    def closeEvent(self, event):

        if self.functions.progressThread.running:
            # TO-DO
            # pickle self.functions.progressThread.torrents for recover on restart
            print('Thread still running.')
        else:
            self.functions.thread.quit()

        if self.functions.post_processing:

            reply = QtWidgets.QMessageBox.question(
                self,
                'Quit',
                """A file is still being processed (<30s left)
                \nAre you sure you want to quit?""",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()


class ScheduleWindow(QtWidgets.QWidget, Ui_Schedule):

    search_title = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.engine = PluginEngine()

        # <Load GUI properties>
        self.clicked = False
        self.frame.setFrameShape(QtWidgets.QFrame.Box)

        # <Connections>
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())
        self.btn_close.clicked.connect(lambda: self.close())
        self.tableViewSchedule.clicked.connect(self.search_clicked)

        self.populate_table()

    def populate_table(self):
        data = self.engine.update_schedule()
        self.model = ScheduleTableModel(data)
        self.tableViewSchedule.setModel(self.model)

        self.tableViewSchedule.verticalHeader().setVisible(False)
        space = self.tableViewSchedule.minimumWidth() - 30
        [self.tableViewSchedule.setColumnWidth(
            col, int(space / 7)) for col in range(7)]

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def search_clicked(self, index):
        self.search_title.emit(self.model.return_selected(index).title)
        self.close()

    # <App Events>
    def mousePressEvent(self, event):
        self.old_pos_x = int(event.screenPos().x())
        self.old_pos_y = int(event.screenPos().y())

    def mouseMoveEvent(self, event):
        if self.clicked:
            dx = self.old_pos_x - int(event.screenPos().x())
            dy = self.old_pos_y - int(event.screenPos().y())
            self.move(self.pos().x() - dx, self.pos().y() - dy)

        self.old_pos_x = int(event.screenPos().x())
        self.old_pos_y = int(event.screenPos().y())
        self.clicked = True

        return QtWidgets.QWidget.mouseMoveEvent(self, event)


class AiringToday(QtWidgets.QWidget, Ui_AiringToday):

    search_title = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.engine = PluginEngine()

        # <Load GUI properties>
        self.clicked = False

        self.bg.setFrameShape(QtWidgets.QFrame.Box)

        self.model = QtGui.QStandardItemModel()
        self.tableViewSchedule.setModel(self.model)

        # <Connections>
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())
        self.btn_close.clicked.connect(lambda: self.close())
        self.tableViewSchedule.clicked.connect(self.search_clicked)
        self.populate_table()

    def setupTable(self):
        self.model.clear()
        self.model.setColumnCount(3)
        self.model.setHorizontalHeaderLabels(['Time', 'Show', 'Score'])
        self.tableViewSchedule.verticalHeader().setVisible(False)
        self.tableViewSchedule.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)

    def populate_table(self):
        self.setupTable()
        data = self.engine.update_schedule(today=True)

        def item(d: AiringAnime):
            title = QtGui.QStandardItem(d.title)
            _time = QtGui.QStandardItem(d.airing_time)
            score = QtGui.QStandardItem(str(d.score))

            return title, _time, score

        [self.model.appendRow(item(show)) for show in data]

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def search_clicked(self, index):
        self.search_title.emit(self.model.itemFromIndex(index).text())
        self.close()

    # <App Events>
    def mousePressEvent(self, event):
        self.old_pos_x = int(event.screenPos().x())
        self.old_pos_y = int(event.screenPos().y())

    def mouseMoveEvent(self, event):
        if self.clicked:
            dx = self.old_pos_x - int(event.screenPos().x())
            dy = self.old_pos_y - int(event.screenPos().y())
            self.move(self.pos().x() - dx, self.pos().y() - dy)

        self.old_pos_x = int(event.screenPos().x())
        self.old_pos_y = int(event.screenPos().y())
        self.clicked = True

        return QtWidgets.QWidget.mouseMoveEvent(self, event)


def launch():
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('ui/fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('ui/fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch()
