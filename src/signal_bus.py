from PySide6.QtCore import QObject, Signal
from typing import Dict

class _WriteFileSignal(QObject):
    """ 介面變更訊號 """
    inPlace = Signal(str, str, dict)
    flatten = Signal(str, str, dict)
    writeFolderToZip = Signal(str, str, dict)

    def __init__(self):
        super().__init__()

class _UiSignal(QObject):
    """ 介面變更訊號 """
    selectionStatusChange = Signal(int)
    comicListSortDisplayChange = Signal(int)
    setProgressBar = Signal(int, int)
    sendCritical = Signal(str, str)
    sendInformation = Signal(str, str)
    retranslateUi = Signal()
    comicListSelectRows = Signal(list)

    def __init__(self):
        super().__init__()

class _AppSettingSignals(QObject):
    """ 應用設定訊號 """
    fontSizeChanged = Signal(int)
    writeModeChanged = Signal(int)
    imageExtChanged = Signal(list)
    allowFilesChanged = Signal(list)
    langChanged = Signal(str)

    def __init__(self):
        super().__init__()

class _DataChangeSignals(QObject):
    """ 資料變更訊號 """
    sourceDirChanged = Signal(str)
    outputDirChanged = Signal(str)
    outputExtChanged = Signal(str)
    fileListChanged = Signal(list)
    fileMetadataCacheChanged = Signal(dict)

    def __init__(self):
        super().__init__()

class _SignalBus(QObject):
    """ 信號總線 """
    fileReadReady = Signal()
    comicListSort = Signal(int)
    selectedComicPath = Signal(list)
    requireInfoEditorInput = Signal()
    returnInfoEditorInput = Signal(dict)
    requireSelectedComic = Signal()
    returnSelectedComic = Signal(dict)
    startProcess = Signal()

    def __init__(self):
        super().__init__()
        self.appSetting = _AppSettingSignals()
        self.dataChange = _DataChangeSignals()
        self.ui = _UiSignal()
        self.writeFile = _WriteFileSignal()

SIGNAL_BUS = _SignalBus()
