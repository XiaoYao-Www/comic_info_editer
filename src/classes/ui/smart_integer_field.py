from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QIntValidator

class SmartIntegerField(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText("-1 = {保留}")
        self.setValidator(QIntValidator(-1, 9999, self))
        self.textChanged.connect(self._on_text_changed)
        self._state = "clear"  # 初始狀態為清除

    def _on_text_changed(self, text: str):
        text = text.strip()
        if text == "{保留}" or text == "-1":
            self._state = "preserve"
        elif text == "":
            self._state = "clear"
        elif text.lstrip("-").isdigit():
            self._state = "value"
        else:
            self._state = "invalid"

    def value(self):
        text = self.text().strip()
        if text == "{保留}" or text == "-1":
            return "{保留}"
        elif text == "":
            return ""
        elif text.lstrip("-").isdigit():
            return int(text)
        else:
            raise ValueError(f"非法輸入：{text}")

    def setValue(self, value):
        if value == "{保留}":
            self._state = "preserve"
            self.setText("{保留}")  # 或改用 "{保留}" 看你習慣
        elif value == "":
            self._state = "clear"
            self.setText("")
        else:
            self._state = "value"
            self.setText(str(value))

    def get_state(self):
        return self._state
