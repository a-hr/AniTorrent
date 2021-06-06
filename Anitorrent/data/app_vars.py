from pathlib import Path
from PyQt5.QtCore import QSettings

class Config:

    __slots__ = (
        'root_folder', 'config_file', 'log_file', 'icon', 'qbittorrent_path', 'download_path',
        'postprocess', 'user_label', 'custom_WebUI', 'user_WebUI', 'pass_WebUI', 'port_WebUI',
        '__settings'
    )

    def __init__(self):
        
        self.root_folder = Path(__file__).resolve().parent.parent
        self.config_file = str(self.root_folder / 'data' / 'config.ini')
        self.log_file = str(self.root_folder / 'data' / 'log.txt')
        self.icon = str(self.root_folder / 'ui' / 'icons' / 'logo.ico')

        self.__settings = QSettings(self.config_file, QSettings.IniFormat)

        # Folders

        self.__settings.beginGroup('Folders')

        self.qbittorrent_path = self.__settings.value('qBittorrent')
        self.download_path = self.__settings.value('Downloads')
        
        self.__settings.endGroup()

        # Settings

        self.__settings.beginGroup('Settings')

        self.postprocess = self.__settings.value('postprocess', type=bool)
        self.user_label = self.__settings.value('userLabel')
        self.custom_WebUI = self.__settings.value('WebUIkeys', type=bool)
        self.user_WebUI = self.__settings.value('user')
        self.pass_WebUI = self.__settings.value('pass')
        self.port_WebUI = self.__settings.value('port', type=int)

        self.__settings.endGroup()

    def save_changes(self, **options):

        # <Folders>
        self.__settings.beginGroup('Folders')
        opt_array = ('qBittorrent', 'Downloads')

        [self.__settings.setValue(opt, val) for opt, val in zip(opt_array, options['val_folders'])]
        
        self.__settings.endGroup()
        # </Folders>

        # <Settings>
        self.__settings.beginGroup('Settings')
        opt_array = ('postprocess', 'userLabel', 'WebUIkeys', 'user', 'pass', 'port')
        
        [self.__settings.setValue(opt, val) for opt, val in zip(opt_array, options['val_settings'])]

        self.__settings.endGroup()
        # </Settings>

        self.__settings.sync()

