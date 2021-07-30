from PyQt5 import QtCore, QtWidgets


class CheckableComboBox(QtWidgets.QComboBox):

    def __init__(self):
        super().__init__()
        self._changed = False
        self.view().pressed.connect(self.handleItemPressed)

    def setItemChecked(self, index, checked=False):
        item = self.model().item(index, self.modelColumn())

        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)

        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
        self._changed = True

    def hidePopup(self):
        if not self._changed:
            super().hidePopup()
        self._changed = False
        
    def returnChecked(self):
        item = lambda index: self.model().item(index, self.modelColumn())
        return [item(index).text()
            for index in range(self.count())
            if item(index).checkState() == QtCore.Qt.Checked]
        