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
## 翻譯
from src.translations import TR

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
        self.font_size_label = QLabel(TR.UI_CONSTANTS["字體大小："]())
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 30)
        self.font_size_spin.setValue(GLOBAL_DATA_STORE.get("font_size")) # 載入初始值

        # 寫入模式切換
        write_mode_layout = QHBoxLayout()
        self.write_mode_label = QLabel(TR.UI_CONSTANTS["寫入模式："]())
        self.write_mode_combo = QComboBox()
        self.write_mode_combo.addItems([
            TR.UI_CONSTANTS["原位置寫入"](),
            TR.UI_CONSTANTS["鋪平寫入"](),
        ])
        self.write_mode_combo.setCurrentIndex(GLOBAL_DATA_STORE.get("write_mode")) # 載入初始值

        # 圖片附檔名
        image_extension_layout = QHBoxLayout()
        self.image_extension_label = QLabel(TR.UI_CONSTANTS["圖片附檔名："]())
        self.image_extension_edit = QLineEdit()
        self.image_extension_edit.setText(', '.join(GLOBAL_DATA_STORE.get("image_exts"))) # 載入初始值

        # 允許檔案
        allow_files_layout = QHBoxLayout()
        self.allow_files_label = QLabel(TR.UI_CONSTANTS["允許檔案："]())
        self.allow_files_edit = QLineEdit()
        self.allow_files_edit.setText(', '.join(GLOBAL_DATA_STORE.get("allow_files"))) # 載入初始值

        # 語言選擇
        lang_select_layout = QHBoxLayout()
        self.lang_select_label = QLabel(TR.UI_CONSTANTS["語言選擇："]())
        self.lang_select_combo = QComboBox()
        self.lang_select_combo.addItems(GLOBAL_DATA_STORE.get("langFileData").keys())
        self.lang_select_combo.setCurrentText(GLOBAL_DATA_STORE.get("selectedLang")) # 載入預設值

        # 結構組合
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        ## 字體大小
        font_size_layout.addWidget(self.font_size_label, stretch=1)
        font_size_layout.addWidget(self.font_size_spin, stretch=4)
        layout.addLayout(font_size_layout)
        ## 寫入模式
        write_mode_layout.addWidget(self.write_mode_label, stretch=1)
        write_mode_layout.addWidget(self.write_mode_combo, stretch=4)
        layout.addLayout(write_mode_layout)
        # 圖片附檔名
        image_extension_layout.addWidget(self.image_extension_label, stretch=1)
        image_extension_layout.addWidget(self.image_extension_edit, stretch=4)
        layout.addLayout(image_extension_layout)
        # 允許檔案
        allow_files_layout.addWidget(self.allow_files_label, stretch=1)
        allow_files_layout.addWidget(self.allow_files_edit, stretch=4)
        layout.addLayout(allow_files_layout)
        # 選擇語言
        lang_select_layout.addWidget(self.lang_select_label, stretch=1)
        lang_select_layout.addWidget(self.lang_select_combo, stretch=4)
        layout.addLayout(lang_select_layout)
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
        # 語言刷新
        # SIGNAL_BUS.ui.retranslateUi.connect(self.retranslateUi)
        # 語言變換顯示
        SIGNAL_BUS.appSetting.langChanged.connect(self.lang_selected_changed_display)

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
        # 語言選擇
        self.lang_select_combo.currentTextChanged.connect(self.write_lang_selected)

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

    def lang_selected_changed_display(self, selectedLang: str) -> None:
        """ 語言選擇變換顯示 """
        with QSignalBlocker(self.lang_select_combo):
            self.lang_select_combo.setCurrentText(selectedLang)

    def write_lang_selected(self, selectedLang: str) -> None:
        """ 寫入語言選擇 """
        GLOBAL_DATA_STORE.set("selectedLang", selectedLang)

    def retranslateUi(self):
        """ UI 語言刷新 """
        self.font_size_label.setText(TR.UI_CONSTANTS["字體大小："]())
        #
        self.write_mode_label.setText(TR.UI_CONSTANTS["寫入模式："]())
        # 刷新 QComboBox 的文字但保留目前選取
        current_index = self.write_mode_combo.currentIndex()
        self.write_mode_combo.clear()
        self.write_mode_combo.addItems([
            TR.UI_CONSTANTS["原位置寫入"](),
            TR.UI_CONSTANTS["鋪平寫入"](),
        ])
        with QSignalBlocker(self.write_mode_combo):
            self.write_mode_combo.setCurrentIndex(current_index)
        #
        self.image_extension_label.setText(TR.UI_CONSTANTS["圖片附檔名："]())
        #
        self.allow_files_label.setText(TR.UI_CONSTANTS["允許檔案："]())
        #
        self.lang_select_label.setText(TR.UI_CONSTANTS["語言選擇："]())