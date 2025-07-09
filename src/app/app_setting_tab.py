from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
from .global_data_store import GlobalDataStore
from .signal_bus import SignalBus

class AppSettingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.store = GlobalDataStore()
        self.init_ui()

    def init_ui(self):
        """ 初始化UI元件 """
        layout = QVBoxLayout()

        # 字體大小設定
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel(self.tr("字體大小："))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 30)
        self.font_size_spin.setValue(10)
        font_size_layout.addWidget(font_size_label, stretch=1)
        font_size_layout.addWidget(self.font_size_spin, stretch=7)
        layout.addLayout(font_size_layout)

        # 寫入模式切換
        write_mode_layout = QHBoxLayout()
        write_mode_label = QLabel(self.tr("寫入模式："))
        self.write_mode_combo = QComboBox()
        self.write_mode_combo.addItems([
            self.tr("原位置寫入"),
            self.tr("鋪平寫入"),
        ])
        self.write_mode_combo.setCurrentIndex(0)
        write_mode_layout.addWidget(write_mode_label, stretch=1)
        write_mode_layout.addWidget(self.write_mode_combo, stretch=7)
        layout.addLayout(write_mode_layout)

        # 向上對其
        layout.addStretch()

        # 加入主 Layout
        self.setLayout(layout)

        # 功能建構
        self.functional_construction()

    def functional_construction(self):
        """ 功能建構 """
        self.font_size_spin.valueChanged.connect(
            lambda value: SignalBus.appSetting.fontSizeChanged.emit(value)
        )
        self.write_mode_combo.currentTextChanged.connect(
            lambda value: self.store.update({
                "write_mode": value,
            })
        )