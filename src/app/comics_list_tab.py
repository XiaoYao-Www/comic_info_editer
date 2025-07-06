from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
import os
from natsort import natsorted
from .global_data_store import GlobalDataStore
from .signal_bus import SignalBus

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
            self.tr("手動")
        ])
        h_action0_0.addWidget(QLabel(self.tr("排序依據：")), stretch=1)
        h_action0_0.addWidget(self.meta_sort_combo, stretch=1)
        h_action0.addLayout(h_action0_0, stretch=1)
        # 間隔
        h_action0.addStretch(5)
        # 已選取狀態
        self.selection_status = QLabel(
            self.tr("已選中 {selected} / 共 {total} 本漫畫").format(
                selected=0,
                total=0
        ))
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
        h_action1.addWidget(self.output_btn, stretch=2)
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

        # 功能建構
        self.functional_construction()

    def functional_construction(self):
        """ 功能建構 """
        # 載入漫畫資料夾
        self.source_btn.clicked.connect(self.select_source_folder)
        # 排序依據
        self.meta_sort_combo.currentTextChanged.connect(self.meta_sort)
        # 列表操作
        self.list_widget.model().rowsMoved.connect(self.on_rows_moved)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

    def select_source_folder(self):
        """ 選擇漫畫資料夾 """
        folder = QFileDialog.getExistingDirectory(self, self.tr("選擇漫畫資料夾"))
        if folder:
            self.store.update({
                "source_dir": folder
            })
            self.source_label.setText(folder)
            self.load_file_list()

    def load_file_list(self):
        """ 載入檔案列表 """
        self.list_widget.clear()
        # 載入
        source_dir = self.store.get("source_dir")
        file_list = []
        file_metadata_cache = {}

        if not os.path.isdir(source_dir):
            return
        
        for root, _, files in os.walk(source_dir):
            for f in files:
                if f.lower().endswith((".zip", ".cbz")):
                    rel_path = os.path.relpath(os.path.join(root, f), source_dir)
                    file_list.append(rel_path)
                    full_path = os.path.join(source_dir, rel_path)
                    # file_metadata_cache[rel_path] = read_comicinfo_xml(full_path)
                    self.list_widget.addItem(rel_path)

        self.store.update({
            "file_list": file_list,
            "file_metadata_cache": file_metadata_cache 
        })
        self.selection_status.setText(
            self.tr("已選中 {selected} / 共 {total} 本漫畫").format(
                selected=0,
                total=self.list_widget.count()
        ))
        self.meta_sort(self.meta_sort_combo.currentText()) # 預先排序

    def meta_sort(self, key):
        """ 依規則排序 """
        file_list = self.store.get("file_list")
        if key == self.tr("檔名"):
            file_list = natsorted(file_list)
        elif key == self.tr("編號"):
            pass
        else:
            return
        # 刷新
        self.store.update({
            "file_list": file_list
        })
        self.list_widget.clear()
        for f in file_list:
            self.list_widget.addItem(f)

    def on_rows_moved(self, parent, start, end, destination, row):
        """ 列表行移動 """
        file_list = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        self.store.update({
            "file_list": file_list
        })
        self.meta_sort_combo.setCurrentText(self.tr("手動"))

    def on_selection_changed(self):
        """ 列表選擇變化 """
        selected = [item.text() for item in self.list_widget.selectedItems()]
        self.selection_status.setText(
            self.tr("已選中 {selected} / 共 {total} 本漫畫").format(
                selected=len(selected),
                total=self.list_widget.count()
        ))

        # 多選資料送編輯器
        # all_data = [self.file_metadata_cache.get(path, {}) for path in selected] if selected else []
        # self.comicinfo_editor.set_data_list(all_data)

        # # 同步更新批次用 metadata (取編輯器當前值)
        # # 由於編輯器更新自己metadata，這邊同步更新
        # self.metadata.update(self.comicinfo_editor.metadata)