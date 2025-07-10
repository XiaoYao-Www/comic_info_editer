from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy,
    QListView
)
from PySide6.QtCore import Qt, QSignalBlocker
import os
# 自訂庫
from src.global_data_store import GLOBAL_DATA_STORE
from src.signal_bus import SIGNAL_BUS
from src.app.model.comic_list_model import ComicListModel

class ComicsListTab(QWidget):
    def __init__(self):
        super().__init__()
        # Model 實例化
        self.comic_list_model = ComicListModel()

        # 初始化 UI
        self.init_ui()

        # 訊號連接
        self.signal_connection()

        # 功能構建
        self.functional_construction()

    ### 初始化函式 ###
    def init_ui(self):
        """ 初始化UI元件 """
        # 載入漫畫資料夾
        source_path_layout = QHBoxLayout()
        self.source_path_btn = QPushButton(self.tr("選擇漫畫資料夾"))
        self.source_path_label = QLabel(self.tr("尚未選擇"))
        ## 建構
        source_path_layout.addWidget(self.source_path_btn, stretch=1)
        source_path_layout.addWidget(self.source_path_label, stretch=4)

        # 功能欄0
        action_layout_0 = QHBoxLayout()
        ## 排序
        list_sort_layout = QHBoxLayout()
        self.list_sort_combo = QComboBox()
        self.list_sort_combo.addItems([
            self.tr("手動"),
            self.tr("檔名"),
            self.tr("編號"),
        ])
        ### 構建
        list_sort_layout.addWidget(QLabel(self.tr("排序依據：")), stretch=1)
        list_sort_layout.addWidget(self.list_sort_combo, stretch=1)
        ## 已選取狀態
        self.selection_status = QLabel(
            self.tr("已選中 {selected} / 共 {total} 本漫畫").format(
                selected=0,
                total=0
        ))
        ## 構建
        action_layout_0.addLayout(list_sort_layout, stretch=1)
        action_layout_0.addStretch(5) # 間隔
        action_layout_0.addWidget(self.selection_status, stretch=1)
       

        # 漫畫列表
        self.comic_list = QListView()
        self.comic_list.setModel(self.comic_list_model)
        self.comic_list.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 多選
        self.comic_list.setDragEnabled(True)           # 可拖曳
        self.comic_list.setAcceptDrops(True)           # 接受拖曳
        self.comic_list.setDropIndicatorShown(True)    # 顯示放置指示
        self.comic_list.setDragDropMode(QListView.InternalMove)  # 僅允許內部拖曳

        # 功能欄1
        action_layout_1 = QHBoxLayout()
        ## 選擇輸出資料夾
        self.output_path_btn = QPushButton(self.tr("選擇輸出資料夾"))
        self.output_path_label = QLabel(self.tr("尚未選擇"))
        ## 副檔名選擇
        ext_layout = QHBoxLayout()
        self.ext_combo = QComboBox()
        self.ext_combo.addItems([
            "cbz", 
            "zip"
        ])
        ### 構建
        ext_layout.addWidget(QLabel(self.tr("輸出副檔名：")), stretch=1)
        ext_layout.addWidget(self.ext_combo, stretch=1)
        ## 構建
        action_layout_1.addWidget(self.output_path_btn, stretch=2)
        action_layout_1.addWidget(self.output_path_label, stretch=6)
        action_layout_1.addLayout(ext_layout, stretch=1)

        # 功能欄2
        action_layout_2 = QHBoxLayout()
        ## 開始按鈕
        self.run_btn = QPushButton(self.tr("開始處理"))
        ## 進度條
        self.progress_bar = QProgressBar()
        ## 構建
        action_layout_2.addWidget(self.run_btn, stretch=1)
        action_layout_2.addWidget(self.progress_bar, stretch=7)

        # 結構組合
        layout = QVBoxLayout()
        layout.addLayout(source_path_layout)
        layout.addLayout(action_layout_0)
        layout.addWidget(self.comic_list)
        layout.addLayout(action_layout_1)
        layout.addLayout(action_layout_2)
        self.setLayout(layout)

    def signal_connection(self):
        """ 訊號連接 """
        # 漫畫資料夾顯示
        SIGNAL_BUS.dataChange.sourceDirChanged.connect(self.source_folder_display)
        # 輸出資料夾顯示
        SIGNAL_BUS.dataChange.outputDirChanged.connect(self.output_folder_display)
        # 副檔名選擇顯示
        SIGNAL_BUS.dataChange.outputExtChanged.connect(self.ext_changed_display)
        # 選擇題示更新
        SIGNAL_BUS.ui.selectionStatusChange.connect(self.selection_status_change)
        # 排序模式顯示改變
        SIGNAL_BUS.ui.comicListSortDisplayChange.connect(self.comic_list_sort_display)
        # 取得選中漫畫
        SIGNAL_BUS.requireSelectedComic.connect(self.get_selected_comic)
        # 進度條更新
        SIGNAL_BUS.ui.setProgressBar.connect(self.set_progress_bar)

    def functional_construction(self):
        """ 功能建構 """
        # 載入漫畫資料夾
        self.source_path_btn.clicked.connect(self.select_source_folder)
        # 選擇輸出資料夾
        self.output_path_btn.clicked.connect(self.select_output_folder)
        # 副檔名選擇
        self.ext_combo.currentTextChanged.connect(self.ext_changed)
        # 漫畫排序改變
        self.list_sort_combo.currentIndexChanged.connect(
            lambda index: SIGNAL_BUS.comicListSort.emit(index)
        )
        # 列表選擇改變
        self.comic_list.selectionModel().selectionChanged.connect(self.comic_list_seletion_changed)
        # 開始處理
        self.run_btn.clicked.connect(
            lambda: SIGNAL_BUS.startProcess.emit()
        )


    ### 功能函式 ###

    def select_source_folder(self) -> None:
        """ 選擇漫畫資料夾 """
        folder = QFileDialog.getExistingDirectory(self, self.tr("選擇漫畫資料夾"))
        if folder:
            GLOBAL_DATA_STORE.update({
                "source_dir": folder
            })

    def source_folder_display(self, text:str) -> None:
        """ 漫畫資料夾顯示 """
        self.source_path_label.setText(text)

    def select_output_folder(self) -> None:
        """ 選擇輸出資料夾 """
        folder = QFileDialog.getExistingDirectory(self, self.tr("選擇輸出資料夾"))
        if folder:
            GLOBAL_DATA_STORE.update({
                "output_dir": folder
            })

    def output_folder_display(self, text:str) -> None:
        """ 輸出資料夾顯示 """
        self.output_path_label.setText(text)

    def ext_changed(self, ext: str) -> None:
        """ 副檔名選擇 """
        GLOBAL_DATA_STORE.update({
            "output_ext": ext,
        })

    def ext_changed_display(self, ext: str) -> None:
        """ 副檔名選擇顯示 """
        with QSignalBlocker(self.ext_combo):
            self.ext_combo.setCurrentText(ext)

    def selection_status_change(self, value: int) -> None:
        """ 更新選擇狀態提式 """
        self.selection_status.setText(
            self.tr("已選中 {selected} / 共 {total} 本漫畫").format(
                selected=value,
                total=len(GLOBAL_DATA_STORE.get("file_list", []))
        ))

    def comic_list_sort_display(self, index:int) -> None:
        """ 排序模式顯示改變 """
        with QSignalBlocker(self.list_sort_combo):
            self.list_sort_combo.setCurrentIndex(index)

    def comic_list_seletion_changed(self, selected, deselected) -> None:
        """ 列表選擇改變 """
        selected_indexes = self.comic_list.selectionModel().selectedIndexes()
        # 變更顯示 ( 不經過訊號 )
        self.selection_status_change(len(selected_indexes))
        # 選中漫畫路徑名
        selected_comic_path = [self.comic_list_model.data(index, Qt.DisplayRole) for index in selected_indexes]
        SIGNAL_BUS.selectedComicPath.emit(selected_comic_path)

    def get_selected_comic(self) -> None:
        """ 取得選中漫畫 """
        selected_indexes = self.comic_list.selectionModel().selectedIndexes()
        selected_comic_data = {}
        for index in selected_indexes:
            path = self.comic_list_model.data(index, Qt.DisplayRole)
            selected_comic_data[path] = index.row()
        SIGNAL_BUS.returnSelectedComic.emit(selected_comic_data)

    def set_progress_bar(self, value: int, max: int) -> None:
        """ 設置進度條顯示 """
        self.progress_bar.setMaximum(max)
        self.progress_bar.setValue(value)