import ctypes
import webbrowser

from data import Config
from PyQt5 import QtCore, QtGui, QtWidgets

from .modules import Ui_MainWindow
from .widgets import CheckableComboBox


class GUI(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

    def ui_init(self):
        self.clicked = False
        self.config = Config()

        # <GUI Properties>
        self.setWindowIcon(QtGui.QIcon(self.config.icon))
        myappid = u"Kajiya_aru.AniTorrent.v1_0_5"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowTitle("AniTorrent")

        startSize = QtCore.QSize(1000, 720)
        self.setFixedSize(startSize)

        self.label_title_bar_top.setText("AniTorrent")
        self.label_credits.setText("Developed by: Kajiya_aru")
        self.label_version.setText("v1.0.5")

        self.setup_menus()
        self.setup_widgets()
        self.setup_settings()

        def moveWindow(event):
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.frame_label_top_btns.mouseMoveEvent = moveWindow

        self.uiDefinitions()

        self.show()

    def setup_menus(self):

        self.btn_toggle_menu.clicked.connect(lambda: self.toggleMenu(220, True))

        self.stackedWidget.setMinimumWidth(20)
        self.addNewMenu(
            "Search",
            "btn_search",
            "url(:/16x16/icons/16x16/cil-magnifying-glass.png)",
            True,
        )
        self.addNewMenu(
            "Results", "btn_results", "url(:/16x16/icons/16x16/cil-browser.png)", True
        )
        self.addNewMenu(
            "Downloads",
            "btn_downloads",
            "url(:/16x16/icons/16x16/cil-data-transfer-down.png)",
            True,
        )
        self.addNewMenu(
            "Settings",
            "btn_settings",
            "url(:/16x16/icons/16x16/cil-settings.png)",
            False,
        )
        self.addNewMenu(
            "About", "btn_about", "url(:/16x16/icons/16x16/cil-people.png)", False
        )

        self.selectStandardMenu("btn_search")
        self.stackedWidget.setCurrentWidget(self.page_home)
        self.labelPage("SEARCH")

    def setup_widgets(self):

        self.combobox_fansubs = CheckableComboBox()
        for index, fansub in enumerate(self.config.plugins):
            self.combobox_fansubs.addItem(fansub[0])
            self.combobox_fansubs.setItemChecked(index, checked=fansub[1])

        self.verticalLayout_10.replaceWidget(
            self.combobox_source, self.combobox_fansubs
        )
        self.combobox_source.close()

        self.tableView_search.verticalHeader().setVisible(False)
        self.tableView_episodes.verticalHeader().setVisible(False)
        self.tableWidget_downloads.verticalHeader().setVisible(False)

        self.tableWidget_downloads.setColumnCount(3)
        self.tableWidget_downloads.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.tableWidget_downloads.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignCenter
        )
        self.tableWidget_downloads.setHorizontalHeaderLabels(
            ("Name", "Progress", "Remaining")
        )

        header = self.tableWidget_downloads.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        with open(self.config.about_md, "r") as ab:
            self.textEdit_About.setHtml(ab.read())
            self.textEdit_About.setEnabled(True)
            self.textEdit_About.setReadOnly(True)

        self.button_GitHub.clicked.connect(
            lambda: webbrowser.open("https://github.com/Kajiya-aru/anitorrent")
        )

    def setup_settings(self):

        self.lineEdit_qB_path.setText(self.config.qbittorrent_path)
        self.lineEdit_download_path.setText(self.config.download_path)

        self.checkBox_cancel_postprocessing.setCheckState(
            QtCore.Qt.Unchecked if self.config.postprocess else QtCore.Qt.Checked
        )

        self.checkBox_custom_WebUi.setCheckState(
            QtCore.Qt.Checked if self.config.custom_WebUI else QtCore.Qt.Unchecked
        )
        self.checkBox_custom_WebUi.stateChanged.connect(
            lambda: self.toggleWebUIState(self.checkBox_custom_WebUi.isChecked())
        )

        self.lineEdit_WebUi_user.setText(self.config.user_WebUI)
        self.lineEdit_WebUi_pass.setText(self.config.pass_WebUI)
        self.lineEdit_WebUi_port.setText(str(self.config.port_WebUI))
        self.toggleWebUIState(self.checkBox_custom_WebUi.isChecked())

    def toggleWebUIState(self, flag):
        self.lineEdit_WebUi_user.setEnabled(flag)
        self.lineEdit_WebUi_pass.setEnabled(flag)
        self.lineEdit_WebUi_port.setEnabled(flag)

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
        button = QtWidgets.QPushButton("1", self)
        button.setObjectName(objName)
        sizePolicy3 = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QtCore.QSize(0, 70))
        button.setLayoutDirection(QtCore.Qt.LeftToRight)
        button.setFont(font)
        button.setStyleSheet(style.replace("ICON_REPLACE", icon))
        button.setText(name)
        button.setToolTip(name)
        button.clicked.connect(self.buttonClickEvent)

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
                self.frame_left_menu, b"minimumWidth"
            )
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()

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
        newText = "| " + text.upper()
        self.label_top_info_2.setText(newText)

    @staticmethod
    def selectMenu(getStyle):
        select = getStyle + ("QPushButton { border-right: 7px solid rgb(44, 49, 60); }")
        return select

    @staticmethod
    def deselectMenu(getStyle):
        deselect = getStyle.replace(
            "QPushButton { border-right: 7px solid rgb(44, 49, 60); }", ""
        )
        return deselect

    @QtCore.pyqtSlot()
    def buttonClickEvent(self):
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
        self.dragPos = event.globalPos()
