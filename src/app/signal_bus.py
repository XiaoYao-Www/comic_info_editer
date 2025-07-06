from PySide6.QtCore import QObject, Signal
from types import SimpleNamespace

class AppSettingSignals(QObject):
    """ 應用設定訊號 """
    fontSizeChanged = Signal(int)

    def __init__(self):
        super().__init__()

class SignalBus_C(QObject):
    """ 信號總線 """
    dataUpdated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.appSetting = AppSettingSignals()

SignalBus = SignalBus_C()
