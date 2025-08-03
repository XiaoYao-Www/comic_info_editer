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
        if not indexes:
            return None
        mime_data = QMimeData()
        if indexes:
            # 取得唯一 row 並排序
            rows = sorted(set(index.row() for index in indexes))
            # 存為逗號分隔字串
            mime_data.setText(",".join(map(str, rows)))
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        """ 拖曳放置行為 """
        if action != Qt.MoveAction or not data.hasText():
            return False

        try:
            source_rows = list(map(int, data.text().split(",")))
        except ValueError:
            return False

        if not source_rows:
            return False

        max_row = self.rowCount()
        if any(r < 0 or r >= max_row for r in source_rows):
            return False

        # 確定目標插入位置
        if row == -1:
            if parent.isValid():
                row = parent.row()
            else:
                row = max_row

        # 排除完全不動作
        if set(source_rows) == set(range(row, row + len(source_rows))):
            return False

        file_list = GLOBAL_DATA_STORE.get("file_list").copy()

        # 保持順序：取得實際要搬移的項目（依照原先順序）
        moving_items = [file_list[r] for r in source_rows]

        # 移除搬移項（注意：由後往前刪，避免 index 位移）
        for r in sorted(source_rows, reverse=True):
            del file_list[r]

        # 調整 row 位置（因為 source_row 被刪後 index 會往前）
        insert_row = row
        for r in source_rows:
            if r < row:
                insert_row -= 1

        # 插入（依原順序）
        for i, item in enumerate(moving_items):
            file_list.insert(insert_row + i, item)

        new_selection_rows = list(range(insert_row, insert_row + len(moving_items)))

        self.beginResetModel()
        GLOBAL_DATA_STORE.update({"file_list": file_list})
        self.endResetModel()

        # 通知 UI 重新選取剛搬過來的項目
        SIGNAL_BUS.ui.comicListSelectRows.emit(new_selection_rows)
        SIGNAL_BUS.ui.comicListSortDisplayChange.emit(0)
        return True

    def notify_data_changed(self, fileList: list):
        """ 通知變更 """
        # 當外部資料改變（但沒有透過 Model 操作），用這個通知 UI 更新
        self.layoutChanged.emit()
