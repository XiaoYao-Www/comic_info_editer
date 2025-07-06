from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
from .global_data_store import GlobalDataStore

class ComicsListTab(QWidget):
    def __init__(self):
        super().__init__()
        self.store = GlobalDataStore()
        self.init_ui()

    def init_ui(self):
        """ 初始化UI元件 """
        layout = QVBoxLayout()

        # 載入漫畫資料夾
        h0 = QHBoxLayout()
        self.source_btn = QPushButton(self.tr("選擇漫畫資料夾"))
        self.source_label = QLabel(self.tr("尚未選擇"))
        h0.addWidget(self.source_btn, stretch=1)
        h0.addWidget(self.source_label, stretch=4)
        layout.addLayout(h0)

        # 功能欄0
        h_action0 = QHBoxLayout()
        # 排序
        h_action0_0 = QHBoxLayout()
        self.meta_sort_combo = QComboBox() # 排序依據
        self.meta_sort_combo.addItems([
            self.tr("檔名"),
            self.tr("編號"),
        ])
        h_action0_0.addWidget(QLabel(self.tr("排序依據：")), stretch=1)
        h_action0_0.addWidget(self.meta_sort_combo, stretch=1)
        h_action0.addLayout(h_action0_0, stretch=1)
        # 間隔
        h_action0.addStretch(5)
        # 已選取狀態
        self.selection_status = QLabel(self.tr("已選中 0 / 共 0 本漫畫"))
        h_action0.addWidget(self.selection_status, stretch=1)
        layout.addLayout(h_action0)

        # 漫畫列表
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(self.list_widget)

        # 功能欄1
        h_action1 = QHBoxLayout()
        # 選擇輸出資料夾
        self.output_btn = QPushButton(self.tr("選擇輸出資料夾"))
        self.output_label = QLabel(self.tr("尚未選擇"))
        # 副檔名選擇
        h_action1_0 = QHBoxLayout()
        self.ext_combo = QComboBox()
        self.ext_combo.addItems([
            self.tr(".cbz"), 
            self.tr(".zip")
        ])
        h_action1_0.addWidget(QLabel(self.tr("輸出副檔名：")), stretch=1)
        h_action1_0.addWidget(self.ext_combo, stretch=1)
        h_action1.addWidget(self.output_btn, stretch=1)
        h_action1.addWidget(self.output_label, stretch=6)
        h_action1.addLayout(h_action1_0, stretch=1)
        layout.addLayout(h_action1)

        # 功能欄2
        h_action2 = QHBoxLayout()
        self.run_btn = QPushButton(self.tr("開始處理"))
        self.progress_bar = QProgressBar()
        h_action2.addWidget(self.run_btn, stretch=1)
        h_action2.addWidget(self.progress_bar, stretch=7)
        layout.addLayout(h_action2)

        # 加入主 Layout
        self.setLayout(layout)