from PySide6.QtCore import QObject, Signal
from types import SimpleNamespace

class _AppSettingSignals(QObject):
    """ 應用設定訊號 """
    fontSizeChanged = Signal(int)
    writeModeChanged = Signal(int)

    def __init__(self):
        super().__init__()

class _SignalBus(QObject):
    """ 信號總線 """

    def __init__(self):
        super().__init__()
        self.appSetting = _AppSettingSignals()

SIGNAL_BUS = _SignalBus()
