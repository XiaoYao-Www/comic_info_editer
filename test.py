from PySide6.QtWidgets import QLayout, QSizePolicy, QWidgetItem
from PySide6.QtCore import QSize, QRect, QPoint


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=5):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self.item_list = []

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        return self.item_list[index] if 0 <= index < len(self.item_list) else None

    def takeAt(self, index):
        return self.item_list.pop(index) if 0 <= index < len(self.item_list) else None

    def expandingDirections(self):
        return 0

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        return size + QSize(
            2 * self.contentsMargins().top(),
            2 * self.contentsMargins().top()
        )

    def _do_layout(self, rect, test_only):
        x, y = rect.x(), rect.y()
        line_height = 0
        for item in self.item_list:
            next_x = x + item.sizeHint().width() + self._spacing
            if next_x - self._spacing > rect.right() and line_height > 0:
                x = rect.x()
                y += line_height + self._spacing
                next_x = x + item.sizeHint().width() + self._spacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()
    
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt


class TagToggleWidget(QWidget):
    def __init__(self, tags: dict[str, str]):
        super().__init__()
        self.setWindowTitle("Tag Selector")
        self.tags = tags
        self.buttons = {}

        # 設定父 widget 的字體大小，子元件會自動繼承
        font = self.font()
        font.setPointSize(14)
        self.setFont(font)

        layout = QVBoxLayout()

        # 使用 FlowLayout 讓按鈕自動換行排列
        self.flow_layout = FlowLayout()
        for display_name, value in self.tags.items():
            btn = QPushButton(display_name)
            btn.setCheckable(True)  # 可切換開關狀態
            self.buttons[display_name] = btn
            self.flow_layout.addWidget(btn)

        layout.addLayout(self.flow_layout)

        self.output_label = QLabel("已啟用標籤值: []")
        layout.addWidget(self.output_label)

        read_btn = QPushButton("讀取選取標籤")
        read_btn.clicked.connect(self.show_selected_tags)
        layout.addWidget(read_btn)

        self.setLayout(layout)

    def get_selected_values(self) -> list[str]:
        return [
            self.tags[display_name]
            for display_name, button in self.buttons.items()
            if button.isChecked()
        ]

    def show_selected_tags(self):
        selected = self.get_selected_values()
        self.output_label.setText(f"已啟用標籤值: {selected}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    tags = {
        "貓咪": "cat", "狗狗": "dog", "鳥類": "bird", "爬蟲": "reptile",
        "兔兔": "rabbit", "倉鼠": "hamster", "刺蝟": "hedgehog", "魚": "fish",
        "123456789": "123"
    }

    window = TagToggleWidget(tags)
    window.resize(500, 300)
    window.show()

    sys.exit(app.exec())
