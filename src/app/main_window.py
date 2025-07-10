from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy,
)
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt
# 自訂庫
from src.signal_bus import SIGNAL_BUS
from src.global_data_store import GLOBAL_DATA_STORE
## tab 導入
from src.app.tabs.app_info_tab import AppInfoTab
from src.app.tabs.app_setting_tab import AppSettingTab
from src.app.tabs.comics_list_tab import ComicsListTab
from src.app.tabs.info_editor_tab import InfoEditorTab

class ComicInfoEditor(QWidget):
    """ 漫畫資訊編輯器 - 主窗口 """
    def __init__(self):
        super().__init__()
        # 初始化 UI
        self.init_ui()

        # 應用設定
        self.setWindowTitle(self.tr("ComicInfo 編輯器"))
        self.resize(900, 750)
        self.change_font_size(GLOBAL_DATA_STORE.get("font_size", 10))

        # 快捷註冊
        self.register_shortcut()

        # 訊號連接
        self.signal_connection()

        
    ### 初始化函式 ###
    def init_ui(self):
        """ UI初始化 """
        # 標籤頁
        self.tabs = QTabWidget()
        self.comics_list_tab = ComicsListTab()
        self.tabs.addTab(self.comics_list_tab, self.tr("列表"))
        self.info_editor_tab = InfoEditorTab()
        self.tabs.addTab(self.info_editor_tab, self.tr("編輯"))
        self.app_setting_tab = AppSettingTab()
        self.tabs.addTab(self.app_setting_tab, self.tr("設定"))
        self.app_info_tab = AppInfoTab()
        self.tabs.addTab(self.app_info_tab, self.tr("關於"))

        # 結構組合
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


    def register_shortcut(self):
        """ 快捷註冊 """
        # tab 下一頁
        self.shortcut_tab_s = QShortcut(QKeySequence("S"), self)
        self.shortcut_tab_alt_s = QShortcut(QKeySequence("Alt+S"), self)
        self.shortcut_tab_alt_s.setContext(Qt.ApplicationShortcut) # 全域化
        # tab 上一頁
        self.shortcut_tab_a = QShortcut(QKeySequence("A"), self)
        self.shortcut_tab_alt_a = QShortcut(QKeySequence("Alt+A"), self)
        self.shortcut_tab_alt_a.setContext(Qt.ApplicationShortcut) # 全域化

    def signal_connection(self):
        """ 信號連接 """
        # 應用設定
        SIGNAL_BUS.appSetting.fontSizeChanged.connect(self.change_font_size)
        # 快捷連結
        self.shortcut_tab_s.activated.connect(self.shortcut_tab_next)
        self.shortcut_tab_alt_s.activated.connect(self.shortcut_tab_next)
        self.shortcut_tab_a.activated.connect(self.shortcut_tab_prev)
        self.shortcut_tab_alt_a.activated.connect(self.shortcut_tab_prev)
        # 訊息框
        SIGNAL_BUS.ui.sendCritical.connect(self.send_critical)
        SIGNAL_BUS.ui.sendInformation.connect(self.send_information)

    ### 功能函式 ###
    def change_font_size(self, size):
        """ 更改字型大小 """
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def shortcut_tab_next(self):
        """ 快捷連結 - tab 下一頁 """
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def shortcut_tab_prev(self):
        """ 快捷連結 - tab 上一頁 """
        self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) if self.tabs.currentIndex() > 0 else self.tabs.count() - 1)

    def send_critical(self, title, text) -> None:
        """ 顯示警告訊息 """
        QMessageBox.critical(self, title, text)

    def send_information(self, title, text) -> None:
        """ 顯示提示訊息 """
        QMessageBox.information(self, title, text)