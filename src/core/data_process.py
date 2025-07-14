from PySide6.QtCore import QObject, Signal, QEventLoop
from PySide6.QtWidgets import (
    QMessageBox, QApplication
)
import os
import zipfile
from typing import Any
# 自訂庫
from src.global_data_store import GLOBAL_DATA_STORE
from src.signal_bus import SIGNAL_BUS
from src.function.comicinfo_process import update_comicinfo_data

class DataProcess(QObject):
    def __init__(self):
        super().__init__()
        # 訊號綁定
        SIGNAL_BUS.startProcess.connect(
            lambda: SIGNAL_BUS.requireInfoEditorInput.emit() # 啟動第一步 - 取得編輯器輸入值
        )
        # 編輯器輸入值回傳
        SIGNAL_BUS.returnInfoEditorInput.connect(self.get_info_editor_input)
        # 選中漫畫回傳
        SIGNAL_BUS.returnSelectedComic.connect(self.get_selected_comic)

    def get_info_editor_input(self, data) -> None:
        """ 取得編輯器資料 """
        self.info_editor_input = data
        # 下一步 - 取得選中漫畫
        SIGNAL_BUS.requireSelectedComic.emit()

    def get_selected_comic(self, data) -> None:
        """ 取得選中漫畫 """
        self.selected_comic = data
        # 下一步 - 啟動執行
        self.start_process()
        
    def start_process(self) -> None:
        # 開始處理
        ## 確保可以執行
        if not GLOBAL_DATA_STORE.get("output_dir"):
            SIGNAL_BUS.ui.sendCritical.emit(self.tr("錯誤"), self.tr("請選擇輸出資料夾"))
            return
        if not GLOBAL_DATA_STORE.get("source_dir"):
            SIGNAL_BUS.ui.sendCritical.emit(self.tr("錯誤"), self.tr("請選擇漫畫資料夾"))
            return
        if not self.selected_comic:
            SIGNAL_BUS.ui.sendInformation.emit(self.tr("提示"), self.tr("請至少選擇一個檔案進行處理"))
            return
        ## 初始化進度條
        SIGNAL_BUS.ui.setProgressBar.emit(0, len(self.selected_comic))
        ## 處理漫畫
        progress_rate = 0
        for rel_path, idx in self.selected_comic.items():
            src_path = os.path.join(GLOBAL_DATA_STORE.get("source_dir"), rel_path)
            out_rel_path = os.path.splitext(rel_path)[0] + f".{GLOBAL_DATA_STORE.get('output_ext')}"
            dst_path = os.path.join(GLOBAL_DATA_STORE.get("output_dir"), out_rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            # 讀取原始 comicInfo（如果存在）
            orig_comic_info = GLOBAL_DATA_STORE.get("file_metadata_cache", {}).get(rel_path, {})

            # 修改 comicInfo
            updated_meta = update_comicinfo_data({
                "fileName": os.path.basename(rel_path).split(".")[0],
                "index": idx + 1
            }, orig_comic_info, self.info_editor_input)

            # 寫入 comicInfo
            if os.path.isdir(src_path):
                # 資料夾
                SIGNAL_BUS.writeFile.writeFolderToZip.emit(src_path, dst_path, updated_meta)
            else:
                # 檔案
                write_mode = GLOBAL_DATA_STORE.get("write_mode")
                if write_mode == 1: # 鋪平寫入
                    SIGNAL_BUS.writeFile.flatten.emit(src_path, dst_path, updated_meta)
                else: # 原位置寫入
                    SIGNAL_BUS.writeFile.inPlace.emit(src_path, dst_path, updated_meta)

            # 更新進度條
            progress_rate += 1
            SIGNAL_BUS.ui.setProgressBar.emit(progress_rate, len(self.selected_comic))
            # 強制刷新
            QApplication.processEvents()

        SIGNAL_BUS.ui.sendInformation.emit(self.tr("完成"), self.tr("所有漫畫處理完成！"))

    
    