from typing import List, TypeVar

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)

Torrent = TypeVar("Torrent")


class SettingsWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.settings_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.setLayout(self.settings_layout)
        self.settings_layout.addLayout(self.form_layout)

        self.save_setts_button = QPushButton("Save", self)
        self.save_setts_button.setObjectName("SaveButton")
        self.settings_layout.addWidget(self.save_setts_button)

        self.cancel_setts_button = QPushButton("Cancel", self)
        self.cancel_setts_button.setObjectName("CancelButton")
        self.settings_layout.addWidget(self.cancel_setts_button)

        for key, value in data.items():
            label = QLabel(key)
            line_edit = QLineEdit(str(value))
            line_edit.setObjectName(f"line_{key}")
            self.form_layout.addRow(label, line_edit)


class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.h_widget = QWidget(self)
        self.h_layout = QHBoxLayout(self.h_widget)

        # Create the search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")

        self.search_button = QPushButton("Search", self)
        self.search_button.setObjectName("SearchButton")

        # Create the table view
        self.table_view = QTableView(self)

        # Add the search bar and table view to the layout
        self.h_layout.addWidget(self.search_bar)
        self.h_layout.addWidget(self.search_button)

        self.layout.addWidget(self.h_widget)
        self.layout.addWidget(self.table_view)


class ResultsWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create the layout for the main widget
        self.results_layout = QHBoxLayout(self)

        # Create the table view to display results
        self.table_view = QTableView(self)

        # Create the right box containing label, combobox, and buttons
        self.right_box = QWidget(self)
        self.right_box.setObjectName("RightBox")

        self.right_box_layout = QVBoxLayout(self.right_box)

        self.label = QLabel("Options", self.right_box)
        self.combo_box = QComboBox(self.right_box)
        self.combo_box.addItems(["Select", "1080p", "720p", "480p"])

        self.checkBox_batch = QCheckBox("Batch", self.right_box)

        self.button_filter = QPushButton("Filter", self.right_box)
        self.button_reset = QPushButton("Reset", self.right_box)
        self.button_download = QPushButton("Download", self.right_box)

        self.right_box_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        self.right_box_layout.addWidget(self.label)
        self.right_box_layout.addWidget(self.combo_box)
        self.right_box_layout.addWidget(self.checkBox_batch)
        self.right_box_layout.addWidget(self.button_filter)
        self.right_box_layout.addWidget(self.button_reset)
        self.right_box_layout.addWidget(self.button_download)

        self.right_box_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Add the table view and the right box to the main layout
        self.results_layout.addWidget(self.table_view)
        self.results_layout.addWidget(self.right_box)


class DownloadsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.torrents = []

        # Create the layout for the widget
        layout = QVBoxLayout(self)

        # Create the table widget to display active downloads
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(3)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.table_widget.setHorizontalHeaderLabels(("Name", "Progress", "ETA"))

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # alignment
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)  # Add this line

        # Add the table widget to the layout
        layout.addWidget(self.table_widget)

    def remove_download(self, file_name):
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).text() == file_name:
                self.table_widget.removeRow(row)
                break

    def update_progress(self, torrents: List[Torrent]):
        # clear table and re-add all torrents
        self.table_widget.clearContents()
        self.table_widget.setRowCount(len(torrents))

        for row, torrent in enumerate(torrents):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(torrent)))
            pb = QProgressBar()
            pb.setValue(torrent.progress)
            pb.setStyleSheet(
                """
                QProgressBar {
                    background-color: rgb(224, 224, 224);
                    border-radius: 1px;
                    text-align: center;
                }
                            
                QProgressBar::chunk {
                    background-color: rgb(85, 170, 255);
                    border-radius: 1px;
                } """
            )
            self.table_widget.setCellWidget(row, 1, pb)
            eta = torrent.eta if not torrent.downloaded else "Processing..."
            self.table_widget.setItem(row, 2, QTableWidgetItem(f"{eta}s"))
