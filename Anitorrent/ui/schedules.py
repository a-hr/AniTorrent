
from models import AiringAnime, ScheduleTableModel
from PyQt5 import QtCore, QtGui, QtWidgets
from tools import PluginEngine

from .modules import Ui_AiringToday, Ui_Schedule


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
