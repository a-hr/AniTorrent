import re
from typing import List, TypeVar

from PyQt5.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel, QModelIndex


Torrent = TypeVar("Torrent")


class SearchTableModel(QAbstractTableModel):
    def __init__(self, data: List[str], fansub: str, language: str) -> None:
        super(SearchTableModel, self).__init__()
        self.HEADERS = ["Title", "Fansub", "Language"]
        self._data = data
        self._fansub = fansub
        self._language = language

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def rowCount(self, *args, **kwargs):
        return len(self._data)

    def columnCount(self, *args, **kwargs):
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]

    def data(self, index, role):
        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return self._data[row]
            elif col == 1:
                return self._fansub
            elif col == 2:
                return self._language

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def return_selected(self, index):
        return self._data[index.row()]


class EpisodeTableModel(QAbstractTableModel):
    def __init__(self, data: List[Torrent]) -> None:
        super(EpisodeTableModel, self).__init__()

        self.HEADERS = ["Title", "Episode", "Quality", "Batch"]
        self._data = data
        self._checked = [False for _ in range(len(data))]

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled

    def rowCount(self, *args, **kwargs):
        return len(self._data)

    def columnCount(self, *args, **kwargs):
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]

    def data(self, index, role):
        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            torrent = self._data[row]
            if col == 0:
                return torrent.series
            elif col == 1:
                return (
                    torrent.episode
                    if not torrent.batch
                    else f"{torrent.episode_start}-{torrent.episode_end}"
                )
            elif col == 2:
                return torrent.quality
            elif col == 3:
                return "true" if torrent.batch else "false"

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.CheckStateRole and col == 0:
            return Qt.Checked if self._checked[row] else Qt.Unchecked

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        if role == Qt.CheckStateRole and col == 0:
            self._checked[row] = True if value == Qt.Checked else False
        self.endInsertRows()
        return True

    def refresh(self):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._checked = [False for _ in range(len(self._data))]
        self.endInsertRows()

    def return_selected(self):
        return [ep for ep, ii in zip(self._data, self._checked) if ii]


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}

    def setFilterByColumn(self, column, regex):
        if isinstance(regex, str):
            regex = re.compile(regex)
        self.filters[column] = regex
        self.invalidateFilter()

    def clearFilter(self, column):
        del self.filters[column]
        self.invalidateFilter()

    def clearFilters(self):
        self.filters = {}
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filters:
            return True

        results = []
        for key, regex in self.filters.items():
            text = ""
            index = self.sourceModel().index(source_row, key, source_parent)
            if index.isValid():
                text = str(self.sourceModel().data(index, Qt.DisplayRole))
                if text is None:
                    text = ""
            results.append(regex.match(text))

        return all(results)
