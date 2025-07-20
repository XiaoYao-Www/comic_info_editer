from PySide6.QtCore import QTranslator, QCoreApplication, QObject
from PySide6.QtWidgets import QApplication
import sys
# 自訂庫
from src.app.main_window import ComicInfoEditor
from src.signal_bus import SIGNAL_BUS
from src.global_data_store import GLOBAL_DATA_STORE

class AppSysCtl(QObject):
    # app 系統調度處理
    def __init__(self):
        super().__init__()

        # 系統應用管理
        self.application = QApplication(sys.argv)
        # 翻譯組件
        self.translator = QTranslator()
        # 應用本體
        self.window = ComicInfoEditor()
        self.window.translator = self.translator

        #訊號連接
        self.signal_connection()

    ### 初始化函數 ###

    def signal_connection(self):
        """ 訊號連接 """
        SIGNAL_BUS.appSetting.langChanged.connect(self.changeLang)

    ### 功能函式 ###

    def changeLang(self, lang: str):
        """ 切換語言 """
        langFile = GLOBAL_DATA_STORE.get("langFileData")[lang]
        self.translator.load(langFile)
        self.application.installTranslator(self.translator)
        SIGNAL_BUS.ui.retranslateUi.emit()
