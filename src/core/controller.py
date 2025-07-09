from PySide6.QtCore import QObject, Signal
from typing import Any, Dict, Optional, Set, Callable
# 自訂庫
from src.signal_bus import SIGNAL_BUS
from src.global_data_store import GLOBAL_DATA_STORE

class BackendCore(QObject):
    def __init__(self):
        super().__init__()
        # 資料集初始化
        GLOBAL_DATA_STORE.update({
            "source_dir": "",
            "output_dir": "",
            "output_ext": "cbz",
            "file_list": [],
            "file_metadata_cache": {},
            "write_mode": 0,
            "font_size": 10,
        })

        # 資料變更追蹤
        GLOBAL_DATA_STORE.subscribe(self.on_data_change)

        # 訊號連接
        self.signal_connection()

    def on_data_change(self, change: Dict[str, Any]) -> None:
        """ 資料變更處理 """
        keys = change.keys()
        if len(keys) == 0 :
            return
        # 字體改變
        if "font_size" in keys:
            SIGNAL_BUS.appSetting.fontSizeChanged.emit(change.get("font_size"))
        # 寫入模式改變
        if "write_mode" in keys:
            SIGNAL_BUS.appSetting.writeModeChanged.emit(change.get("write_mode"))

    def signal_connection(self) -> None:
        """ 訊號連接 """
        pass

