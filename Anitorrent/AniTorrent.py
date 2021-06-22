import sys

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication

from .__main__ import MainWindow


def launch():
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont('ui/fonts/segoeui.ttf')
    QFontDatabase.addApplicationFont('ui/fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch()