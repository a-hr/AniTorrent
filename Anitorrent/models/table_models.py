import re

from PyQt5.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QItemDelegate, QProgressBar, QAbstractItemDelegate

from models import Episode, Torrent


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
            text = ''
            index = self.sourceModel().index(source_row, key, source_parent)
            if index.isValid():
                text = self.sourceModel().data(index, Qt.DisplayRole)
                if text is None:
                    text = ''
            results.append(regex.match(text))

        return all(results)


class EpisodeTableModel(QAbstractTableModel):

    def __init__(
        self,
        episode_list: list[Episode],
        config
        ) -> None:
        
        super(EpisodeTableModel, self).__init__()
        
        self.HEADERS = ['Title', 'Quality', 'Full Season', 'Extra Info']
        self.episodes = episode_list
        self.checked = [False for _ in range(len(self.episodes))]
        self.__config = config

    def flags(self, index):

        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        
        return Qt.ItemIsEnabled

    def rowCount(self, *args, **kwargs):
        return len(self.episodes)

    def columnCount(self, *args, **kwargs):
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]

    def data(self, index, role):

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            episode = self.episodes[row]

            if col == 0:
                return episode.title
            
            elif col == 1:
                return episode.quality
            
            elif col == 2:
                return episode.batch

            elif col == 3:
                return episode.episode_str

        elif role == Qt.TextAlignmentRole and col != 0:
            return Qt.AlignCenter

        elif role == Qt.CheckStateRole and col == 0:
            return Qt.Checked if self.checked[row] else Qt.Unchecked
            
    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        if role == Qt.CheckStateRole and col == 0:
            self.checked[row] = True if value == Qt.Checked else False
        return True     

    # ------ CUSTOMS ------
    def returnSelected(self) -> Torrent:
        return [self.__to_torrent(ep) for ep, ii in zip(self.episodes, self.checked) if ii]

    def __to_torrent(self, ep_obj:Episode) -> Torrent:
        return Torrent(ep_obj, self.__config)

    def refresh(self):
        self.checked = [False for _ in range(len(self.episodes))]
        self.layoutChanged.emit()

