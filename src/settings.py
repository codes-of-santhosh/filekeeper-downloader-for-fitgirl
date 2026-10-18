from PySide6.QtCore import QSettings

class AppSettings:
    def __init__(self):
        self.settings = QSettings("FileKeeperBatchDownloader", "App")
        
    def get_download_dir(self):
        return self.settings.value("download_dir", "")
        
    def set_download_dir(self, directory: str):
        self.settings.setValue("download_dir", directory)
        
    def get_max_concurrent(self):
        return int(self.settings.value("max_concurrent", 3))
        
    def set_max_concurrent(self, val: int):
        self.settings.setValue("max_concurrent", val)
        
    def get_speed_limit_index(self):
        return int(self.settings.value("speed_limit_index", 0))
        
    def set_speed_limit_index(self, val: int):
        self.settings.setValue("speed_limit_index", val)
        
    def get_last_paste_url(self):
        return self.settings.value("last_paste_url", "")
        
    def set_last_paste_url(self, url: str):
        self.settings.setValue("last_paste_url", url)
