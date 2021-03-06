from pathlib import Path
from PyQt5.QtCore import QSettings


class Config:

    __slots__ = (
        "root_folder",
        "config_file",
        "log_file",
        "backup_file",
        "schedule_backup",
        "about_md",
        "icon",
        "qbittorrent_path",
        "download_path",
        "postprocess",
        "custom_WebUI",
        "user_WebUI",
        "pass_WebUI",
        "port_WebUI",
        "plugins",
        "__settings",
    )

    def __init__(self):

        self.root_folder = Path(__file__).resolve().parent.parent
        self.config_file = str(self.root_folder / "data" / "config.ini")
        self.log_file = str(self.root_folder / "data" / "log.txt")
        self.backup_file: Path = self.root_folder / "data" / "__backup"
        self.schedule_backup: Path = self.root_folder / "data" / "schedule.json"
        self.about_md: Path = self.root_folder / "data" / "ABOUT"
        self.icon = str(self.root_folder / "ui" / "icons" / "logo.ico")

        self.__settings = QSettings(self.config_file, QSettings.IniFormat)

        # Folders

        self.__settings.beginGroup("Folders")

        self.qbittorrent_path = self.__settings.value("qBittorrent")
        self.download_path = self.__settings.value("Downloads")

        self.__settings.endGroup()

        # Settings

        self.__settings.beginGroup("Settings")

        self.postprocess = self.__settings.value("postprocess", type=bool)
        self.custom_WebUI = self.__settings.value("WebUIkeys", type=bool)
        self.user_WebUI = self.__settings.value("user")
        self.pass_WebUI = self.__settings.value("pass")
        self.port_WebUI = self.__settings.value("port", type=int)

        self.__settings.endGroup()

        # Defaults
        self.__settings.beginGroup("Defaults")

        self.plugins = []

        # self.__settings.value('SubsPlease', type=bool)))
        self.plugins.append(("SubsPlease", True))
        self.plugins.append(("EraiRaws", self.__settings.value("EraiRaws", type=bool)))
        self.plugins.append(("Judas", self.__settings.value("Judas", type=bool)))
        self.plugins.append(
            ("HorribleSubs", self.__settings.value("HorribleSubs", type=bool))
        )

        self.__settings.endGroup()

    def save_changes(self, **options):

        # <Folders>
        self.__settings.beginGroup("Folders")
        opt_array = ("qBittorrent", "Downloads")

        [
            self.__settings.setValue(opt, val)
            for opt, val in zip(opt_array, options["val_folders"])
        ]

        self.__settings.endGroup()
        # </Folders>

        # <Settings>
        self.__settings.beginGroup("Settings")
        opt_array = ("postprocess", "WebUIkeys", "user", "pass", "port")

        [
            self.__settings.setValue(opt, val)
            for opt, val in zip(opt_array, options["val_settings"])
        ]

        self.__settings.endGroup()
        # </Settings>

        self.__settings.sync()
