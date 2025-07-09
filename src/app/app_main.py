from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
from .signal_bus import SignalBus
from .global_data_store import GlobalDataStore
from .comics_list_tab import ComicsListTab
from .info_editor_tab import InfoEditorTab
from .app_setting_tab import AppSettingTab
from .app_info_tab import AppInfoTab


class ComicInfoEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("ComicInfo 編輯器"))
        self.store = GlobalDataStore()
        self.store.update({
            "source_dir": "",
            "output_dir": "",
            "output_ext": ".cbz",
            "file_list": [],
            "file_metadata_cache": {},
        })

        # 初始化 UI
        self.init_ui()

        # 信號連接
        SignalBus.appSetting.fontSizeChanged.connect(self.change_font_size)

    def init_ui(self):
        """ 初始化UI元件 """
        layout = QVBoxLayout()

        # 標籤頁
        self.tabs = QTabWidget()
        self.comic_list_tab = ComicsListTab()
        self.info_editor_tab = InfoEditorTab()
        self.app_setting_tab = AppSettingTab()
        self.app_info_tab = AppInfoTab()
        self.tabs.addTab(self.comic_list_tab, self.tr("列表"))
        self.tabs.addTab(self.info_editor_tab, self.tr("編輯器"))
        self.tabs.addTab(self.app_setting_tab, self.tr("設定"))
        self.tabs.addTab(self.app_info_tab, self.tr("資訊"))

        # 加入主 Layout
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        # 視窗設定
        self.resize(900, 750)
        self.change_font_size(10)

    def change_font_size(self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

