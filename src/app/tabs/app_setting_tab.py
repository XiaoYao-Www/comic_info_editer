from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSignalBlocker
# 自訂庫
from src.signal_bus import SIGNAL_BUS
from src.global_data_store import GLOBAL_DATA_STORE

class AppSettingTab(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化 UI
        self.init_ui()

        # 訊號連接
        self.signal_connection()

        # 功能架構
        self.functional_construction()

    ### 初始化函式 ###

    def init_ui(self):
        """ 初始化UI元件 """
        # 字體大小設定
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel(self.tr("字體大小："))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 30)
        self.font_size_spin.setValue(GLOBAL_DATA_STORE.get("font_size")) # 載入初始值

        # 寫入模式切換
        write_mode_layout = QHBoxLayout()
        write_mode_label = QLabel(self.tr("寫入模式："))
        self.write_mode_combo = QComboBox()
        self.write_mode_combo.addItems([
            self.tr("原位置寫入"),
            self.tr("鋪平寫入"),
        ])
        self.write_mode_combo.setCurrentIndex(GLOBAL_DATA_STORE.get("write_mode")) # 載入初始值

        # 圖片附檔名
        image_extension_layout = QHBoxLayout()
        image_extension_label = QLabel(self.tr("圖片附檔名："))
        self.image_extension_edit = QLineEdit()
        self.image_extension_edit.setText(', '.join(GLOBAL_DATA_STORE.get("image_exts"))) # 載入初始值

        # 允許檔案
        allow_files_layout = QHBoxLayout()
        allow_files_label = QLabel(self.tr("允許檔案："))
        self.allow_files_edit = QLineEdit()
        self.allow_files_edit.setText(', '.join(GLOBAL_DATA_STORE.get("allow_files"))) # 載入初始值

        # 結構組合
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        ## 字體大小
        font_size_layout.addWidget(font_size_label, stretch=1)
        font_size_layout.addWidget(self.font_size_spin, stretch=4)
        layout.addLayout(font_size_layout)
        ## 寫入模式
        write_mode_layout.addWidget(write_mode_label, stretch=1)
        write_mode_layout.addWidget(self.write_mode_combo, stretch=4)
        layout.addLayout(write_mode_layout)
        # 圖片附檔名
        image_extension_layout.addWidget(image_extension_label, stretch=1)
        image_extension_layout.addWidget(self.image_extension_edit, stretch=4)
        layout.addLayout(image_extension_layout)
        # 允許檔案
        allow_files_layout.addWidget(allow_files_label, stretch=1)
        allow_files_layout.addWidget(self.allow_files_edit, stretch=4)
        layout.addLayout(allow_files_layout)
        ## 主要輸出
        self.setLayout(layout)

    def signal_connection(self):
        """ 訊號連接 """
        # 字體大小變換
        SIGNAL_BUS.appSetting.fontSizeChanged.connect(self.font_size_changed_display)
        # 寫入模式變換
        SIGNAL_BUS.appSetting.writeModeChanged.connect(self.write_mode_changed_display)
        # 圖片附檔名變換
        SIGNAL_BUS.appSetting.imageExtChanged.connect(self.image_extension_changed_display)
        # 允許檔案變換
        SIGNAL_BUS.appSetting.allowFilesChanged.connect(self.allow_files_changed_display)

    def functional_construction(self):
        """ 功能架構 """
        # 字體大小變換
        self.font_size_spin.valueChanged.connect(self.write_font_size)
        # 寫入模式變換
        self.write_mode_combo.currentIndexChanged.connect(self.write_write_mode)
        # 圖片副檔名
        self.image_extension_edit.textChanged.connect(self.write_image_extension)
        # 允許檔案
        self.allow_files_edit.textChanged.connect(self.write_allow_files)

    ### 功能函式 ###
    def write_font_size(self, font_size: int) -> None:
        """ 字體大小寫入 """
        GLOBAL_DATA_STORE.set("font_size", font_size)

    def write_write_mode(self, write_mode: int) -> None:
        """ 寫入模式寫入 """
        GLOBAL_DATA_STORE.set("write_mode", write_mode)

    def font_size_changed_display(self, font_size: int) -> None:
        """ 字體大小變換顯示 """
        with QSignalBlocker(self.font_size_spin):
            self.font_size_spin.setValue(font_size)

    def write_mode_changed_display(self, write_mode: int) -> None:
        """ 寫入模式變換顯示 """
        with QSignalBlocker(self.write_mode_combo):
            self.write_mode_combo.setCurrentIndex(write_mode)

    def image_extension_changed_display(self, image_exts: list[str]) -> None:
        """ 圖片附檔名變換顯示 """
        with QSignalBlocker(self.image_extension_edit):
            self.image_extension_edit.setText(', '.join(image_exts))

    def allow_files_changed_display(self, allow_files: list[str]) -> None:
        """ 允許檔案變換顯示 """
        with QSignalBlocker(self.allow_files_edit):
            self.allow_files_edit.setText(', '.join(allow_files))

    def write_image_extension(self, image_exts: str) -> None:
        """ 圖片附檔名寫入 """
        GLOBAL_DATA_STORE.set("image_exts", [item.strip() for item in image_exts.split(',')])

    def write_allow_files(self, allow_files: str) -> None:
        """ 允許檔案寫入 """
        GLOBAL_DATA_STORE.set("allow_files", [item.strip() for item in allow_files.split(',')])