from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt
import os
from natsort import natsorted
from .global_data_store import GlobalDataStore
from .signal_bus import SignalBus
from ..function import read_comicinfo_xml, write_comicinfo_in_place, write_comicinfo_flatten

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
        # 輸出資料夾
        self.output_btn.clicked.connect(self.select_output_folder)
        # 副檔名選擇
        self.ext_combo.currentTextChanged.connect(self.on_ext_changed)
        # 開始處理
        self.run_btn.clicked.connect(
            lambda : SignalBus.getMetadata.emit()
        )
        # 接收資料
        SignalBus.metadataUpdated.connect(self.run_process)

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
                    file_metadata_cache[rel_path] = read_comicinfo_xml(full_path) # 載入 metadata 快取
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
            file_metadata_cache = self.store.get("file_metadata_cache")
            file_list = sorted(
                            file_list,
                            key=lambda x: int(
                                file_metadata_cache
                                    .get(x, {})
                                    .get("_fields", {})
                                    .get("base", {})
                                    .get("Number", len(file_list) + 1)
                                )
                        )
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
        all_data = [self.store.get("file_metadata_cache", {}).get(path, {}) for path in selected] if selected else []
        SignalBus.comicSelected.emit(all_data)

        # # 同步更新批次用 metadata (取編輯器當前值)
        # # 由於編輯器更新自己metadata，這邊同步更新
        # self.metadata.update(self.comicinfo_editor.metadata)

    def select_output_folder(self):
        """ 選擇輸出資料夾 """
        folder = QFileDialog.getExistingDirectory(self, self.tr("選擇輸出資料夾"))
        if folder:
            self.store.update({
                "output_dir": folder
            })
            self.output_label.setText(folder)

    def on_ext_changed(self, ext):
        """ 副檔名選擇 """
        self.store.update({
            "output_ext": ext
        })

    def resolve_placeholders(self, template: str, context: dict) -> str:
        """ 解析佔位符模板內容 """
        if not isinstance(template, str):
            return template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            template = template.replace(placeholder, str(value))
        return template


    def update_comicinfo_data(self, context: dict, original: dict, updated: dict) -> dict:
        """
        將 get_metadata() 的資料更新回 parse_comicinfo() 的結果中
        僅針對 _fields/base 做更新
        """
        # 預設值
        original.setdefault('_fields', {'base': {}})
        original.setdefault('_complex', {})
        original.setdefault('_nsmap', {})
        # 處理
        for prefix, fields in updated.get('_fields', {}).items():
            if prefix not in original['_fields']:
                original['_fields'][prefix] = {}
            for key, val in fields.items():
                original['_fields'][prefix][key] = self.resolve_placeholders(val, context)

        return original


    def run_process(self, metadata):
        """ 開始處理 """
        selected_items = [item.text() for item in self.list_widget.selectedItems()]
        if not self.store.get("output_dir"):
            QMessageBox.critical(self, "錯誤", "請選擇輸出資料夾")
            return
        if not self.store.get("source_dir"):
            QMessageBox.critical(self, "錯誤", "請選擇漫畫資料夾")
            return
        if not selected_items:
            QMessageBox.information(self, "提示", "請至少選擇一個檔案進行處理")
            return

        self.progress_bar.setMaximum(len(selected_items))
        self.progress_bar.setValue(0)

        for idx, rel_path in enumerate(selected_items, start=1):
            src_path = os.path.join(self.store.get("source_dir"), rel_path)
            out_rel_path = os.path.splitext(rel_path)[0] + self.store.get("output_ext")
            dst_path = os.path.join(self.store.get("output_dir"), out_rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            # 讀取原始 metadata（如果存在）
            orig_meta = self.store.get("file_metadata_cache", {}).get(rel_path, {})

            # 修改 metadata
            item = self.list_widget.findItems(rel_path, Qt.MatchExactly)[0]
            updated_meta = self.update_comicinfo_data({
                "fileName": os.path.basename(rel_path).split(".")[0],
                "index": self.list_widget.row(item) + 1
            }, orig_meta, metadata)

            # 寫入 metadata
            write_mode = self.store.get("write_mode")
            if write_mode == self.tr("鋪平寫入"):
                write_comicinfo_flatten(src_path, dst_path, updated_meta)
            else:
                write_comicinfo_in_place(src_path, dst_path, updated_meta)

            # 更新進度條
            self.progress_bar.setValue(self.progress_bar.value() + 1)
            QApplication.processEvents()

        QMessageBox.information(self, "完成", "所有漫畫處理完成！")