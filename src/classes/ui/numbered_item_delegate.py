from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PySide6.QtCore import Qt, QRect

class NumberedItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # 保存畫筆狀態
        painter.save()

        # 獲取數據並生成顯示文本
        original_text = index.model().data(index, Qt.DisplayRole)
        row_number = index.row() + 1
        display_text = f"{row_number:04d}. {original_text}"

        # 初始化繪製選項
        new_option = QStyleOptionViewItem(option)
        self.initStyleOption(new_option, index)
        new_option.text = ""  # 清空文本，稍後手動繪製

        # 繪製背景（包括選中高亮）
        style = new_option.widget.style() if new_option.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, new_option, painter, new_option.widget)

        # 設置文本顏色
        if option.state & QStyle.State_Selected:
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())

        # 調整文本繪製區域（添加邊距）
        text_rect = option.rect.adjusted(5, 0, -5, 0)

        # 繪製文本
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, display_text)

        # 恢復畫筆狀態
        painter.restore()