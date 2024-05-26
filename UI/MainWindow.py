from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)
from qtawesome import icon
from .windows import SettingsWindow, SearchWidget, ResultsWidget, DownloadsWidget


class MainWindow(QMainWindow):
    def __init__(self, settings: object):
        super().__init__()
        self.setWindowTitle("AniTorrent")
        self.setWindowIcon(QIcon("app-store.png"))
        self.setCentralWidget(QWidget())
        self.setMinimumSize(850, 600)

        self.settings = settings

        font = QFont("Roboto")
        QApplication.setFont(font)

        self.primary_layout = QVBoxLayout(self.centralWidget())
        self.primary_layout.setObjectName("PrimaryLayout")
        self.secondary_layout = QHBoxLayout()

        # Create the top section
        self.top_section = QWidget(self)
        self.top_layout = QVBoxLayout(self.top_section)

        # Create the top banner
        self.banner = QLabel("AniTorrent", self)
        self.banner.setObjectName("Banner")
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setMaximumHeight(int(self.height() * 0.1))
        self.banner.setFont(QFont("Roboto", int(self.width() * 0.04)))
        self.top_layout.addWidget(self.banner)

        # ---------- CREATE WINDOWS ----------
        # Create stacked widget
        self.stacked_widget = QStackedWidget(self)

        # Create stacked windows
        for i in range(4):
            window = QWidget()
            layout = QVBoxLayout(window)
            layout.setObjectName(f"window{i+1}_layout")
            self.stacked_widget.addWidget(window)
            setattr(self, f"window{i+1}_layout", layout)

        # Add download window widgets
        self.search_widget = SearchWidget()
        self.window1_layout.addWidget(self.search_widget)

        # Add results window widgets
        self.results_widget = ResultsWidget()
        self.results_widget.right_box.setMaximumHeight(int(self.height() * 0.4))
        self.results_widget.right_box.setMaximumWidth(int(self.width() * 0.3))
        self.window2_layout.addWidget(self.results_widget)

        # Add downloads window widgets
        self.downloads_widget = DownloadsWidget()
        self.window3_layout.addWidget(self.downloads_widget)

        # Add settings window widgets
        self.settings_window = SettingsWindow(self.settings.config)
        self.window4_layout.addWidget(self.settings_window)

        # Adjust line edits to be the same width
        for key, _ in self.settings.config.items():
            line_edit = self.settings_window.findChild(QLineEdit, f"line_{key}")
            line_edit.setMinimumWidth(int(self.width() * 0.4))

        # ---------- END CREATE WINDOWS ----------

        # ---------- CREATE SIDEBAR AND BUTTONS ----------

        # Create a sidebar
        self.sidebar = QWidget(self)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        # Create buttons with FontAwesome icons
        icon_size = int(self.width() * 0.035)
        icons = ("fa.search", "fa.list-alt", "fa.download", "fa.cog")

        for i, icon_name in enumerate(icons):
            button = QPushButton(icon(icon_name), "", self.sidebar)
            button.setObjectName("SidebarButton")
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setIconSize(QSize(icon_size, icon_size))
            setattr(self, f"button{i+1}", button)

        # Add buttons to the sidebar
        alignment = (Qt.AlignTop, Qt.AlignTop, Qt.AlignTop, Qt.AlignBottom)
        for i, al in enumerate(alignment):
            self.sidebar_layout.addWidget(getattr(self, f"button{i+1}"), alignment=al)

        self.button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.button3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.button4.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        # ---------- END CREATE SIDEBAR AND BUTTONS ----------

        # ---------- ADD FINAL LAYOUTS ----------
        # Add the sidebar and stacked widget to the top layout
        self.secondary_layout.addWidget(self.sidebar)
        self.secondary_layout.addWidget(self.stacked_widget)

        # Add the top section and footer to the main layout
        self.primary_layout.addWidget(self.top_section)
        self.primary_layout.addLayout(self.secondary_layout)

        # Create the footer
        self.footer = QLabel("@a-hr", self)
        self.footer.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.primary_layout.addWidget(self.footer)

        # Show the initial window
        self.stacked_widget.setCurrentIndex(0)

    def resizeEvent(self, event):
        # Resize sidebar
        self.sidebar.setMaximumWidth(int(self.width() * 0.08))
        self.sidebar.setMaximumHeight(int(self.height() * 0.45))

        # Resize banner
        self.banner.setMaximumHeight(int(self.height() * 0.1))
        self.banner.setFont(QFont("Roboto", int(self.width() * 0.04)))

        # Resize sidebar buttons
        icon_size = int(self.width() * 0.035)
        for i in range(4):
            getattr(self, f"button{i+1}").setIconSize(QSize(icon_size, icon_size))

        # Adjust line edits to be the same width
        for key, _ in self.settings.config.items():
            line_edit = self.settings_window.findChild(QLineEdit, f"line_{key}")
            line_edit.setMinimumWidth(int(self.width() * 0.4))

        super().resizeEvent(event)
