from PySide6.QtCore import QAbstractListModel, Qt, QMimeData, QModelIndex, QObject, Signal
from typing import Any
# 自訂庫
from src.global_data_store import GLOBAL_DATA_STORE
from src.signal_bus import SIGNAL_BUS

class ComicListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        # 信號連結
        SIGNAL_BUS.dataChange.fileListChanged.connect(self.notify_data_changed)

    def rowCount(self, parent=QModelIndex()) -> int:
        """ 回覆資料列數 """
        # 告訴 QListView 有幾列（幾筆資料）
        return len(GLOBAL_DATA_STORE.get("file_list"))

    def data(self, index, role) -> str | None:
        """ 回復顯示值 """
        # 告訴 View：第 index.row() 列要顯示什麼
        if role == Qt.DisplayRole:
            return GLOBAL_DATA_STORE.get("file_list")[index.row()]
        return None

    def flags(self, index) -> Any:
        """ 每列行為定義 """
        # 定義每列的行為：可以選取、拖曳、放下
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def supportedDropActions(self) -> Any:
        """ 拖曳行為定義 """
        # 允許的拖曳動作：這裡只支援「移動」
        return Qt.MoveAction

    def mimeTypes(self) -> list:
        """ 拖曳時的資料格式 """
        # 自訂 MIME 格式（拖曳時的資料格式）
        return ['text/plain']

    def mimeData(self, indexes):
        """ 拖曳資料生成 """
        # 拖曳時，打包索引成文字格式傳送
        mime_data = QMimeData()
        if indexes:
            mime_data.setText(str(indexes[0].row()))
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        """ 拖曳放置行為 """
        if action != Qt.MoveAction or not data.hasText():
            return False

        try:
            source_row = int(data.text())
        except ValueError:
            return False

        if source_row < 0 or source_row >= self.rowCount():
            return False

        if row == -1:
            if parent.isValid():
                # ✅ 拖曳到某個項目上：改用那一項的 row 作為目標
                row = parent.row()
            else:
                # 拖曳到空白處：插入最後
                row = self.rowCount()

        # 拖曳到原位或相鄰位 → 無需處理
        if row == source_row or row == source_row + 1:
            return False

        file_list = GLOBAL_DATA_STORE.get("file_list").copy()

        self.beginMoveRows(QModelIndex(), source_row, source_row, QModelIndex(), row)

        item = file_list.pop(source_row)
        if row > source_row:
            row -= 1
        file_list.insert(row, item)

        self.endMoveRows()

        GLOBAL_DATA_STORE.update({"file_list": file_list})
        # 排序模式改變 - 手動
        SIGNAL_BUS.ui.comicListSortDisplayChange.emit(0)
        return True

    def notify_data_changed(self, fileList: list):
        """ 通知變更 """
        # 當外部資料改變（但沒有透過 Model 操作），用這個通知 UI 更新
        self.layoutChanged.emit()
