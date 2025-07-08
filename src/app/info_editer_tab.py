from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy,
    QToolButton
)
from PySide6.QtCore import Qt
from .global_data_store import GlobalDataStore
from ..setting import schema_config
from .signal_bus import SignalBus

class InfoEditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.store = GlobalDataStore()
        self.editors = {}
        self.init_ui()

    def init_ui(self):
        """ 初始化UI元件 """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for section_key, fields in schema_config.items():
            toggle_button = QToolButton(text=self.tr(section_key), checkable=True, checked=True)
            toggle_button.setStyleSheet("QToolButton { border: none; }")
            toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            toggle_button.setArrowType(Qt.DownArrow)

            content_area = QWidget()
            content_layout = QVBoxLayout()
            content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            content_area.setLayout(content_layout)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(content_area)

            def make_toggle_func(button=toggle_button, area=scroll):
                return lambda checked: (button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow), area.setVisible(checked))

            toggle_button.toggled.connect(make_toggle_func())

            layout.addWidget(toggle_button)
            layout.addWidget(scroll)

            for field_key, field_cfg in fields.items():
                hlayout = QHBoxLayout()
                label = QLabel(self.tr(field_cfg["label"]))
                hlayout.addWidget(label, stretch=1)

                widget_cls = field_cfg["type"]
                if widget_cls == QComboBox:
                    widget = QComboBox()
                    # widget.addItems(field_cfg.get("options", ["Unknown", "Yes", "No"]))
                elif widget_cls == QSpinBox:
                    widget = QSpinBox()
                    # widget.setMinimum(field_cfg.get("min", -9999))
                    # widget.setMaximum(field_cfg.get("max", 9999))
                elif widget_cls == QTextEdit:
                    widget = QTextEdit()
                else:
                    widget = widget_cls()

                hlayout.addWidget(widget, stretch=7)
                content_layout.addLayout(hlayout)
                self.editors[field_cfg["info_key"]] = widget

        # 加入主 Layout
        self.setLayout(layout)

        # 功能建構
        self.functional_construction()

    def functional_construction(self):
        """ 功能建構 """
        SignalBus.comicSelected.connect(self.set_data_list)
        SignalBus.getMetadata.connect(self.get_metadata)

    def set_data_list(self, data_list: list[dict]):
        """
        多筆資料設定：若欄位值一致就顯示該值，否則顯示 {保留}
        """
        self.current_data_list = data_list
        self.updating_fields = True
        try:
            for section, fields in schema_config.items():
                for field_key, field_cfg in fields.items():
                    info_key = field_cfg["info_key"]
                    values = []

                    for d in data_list:
                        # 每筆資料從 _fields 中抓取對應欄位
                        val = d.get('_fields', {}).get('base', {}).get(info_key, "")
                        values.append(val)

                    if not values:
                        display_val = ""
                    elif all(v == values[0] for v in values):
                        display_val = values[0]
                    else:
                        display_val = "{保留}"

                    editor = self.editors.get(info_key)
                    if isinstance(editor, QComboBox):
                        idx = editor.findText(display_val)
                        if idx == -1:
                            idx = editor.findText("Unknown")
                        editor.setCurrentIndex(idx)
                    elif isinstance(editor, QTextEdit):
                        editor.setPlainText(display_val)
                    elif isinstance(editor, QSpinBox):
                        if display_val == "{保留}" or display_val == "":
                            editor.setSpecialValueText("{保留}")
                            editor.setValue(editor.minimum())
                        else:
                            editor.setSpecialValueText("")
                            try:
                                editor.setValue(int(display_val))
                            except ValueError:
                                editor.setValue(editor.minimum())
                    else:
                        editor.setText(display_val)
        finally:
            self.updating_fields = False

    def get_metadata(self):
        """ 從 UI 控件取得欄位內容，產生 ComicInfo-compatible 的 dict """
        result = {'_fields': {'base': {}}}
        for section, fields in schema_config.items():
            for field_key, field_cfg in fields.items():
                info_key = field_cfg["info_key"]
                editor = self.editors.get(info_key)
                if isinstance(editor, QComboBox):
                    val = editor.currentText()
                    if val == "{保留}":
                        continue
                    elif val == "":
                        continue
                    result['_fields']['base'][info_key] = editor.currentText()
                elif isinstance(editor, QTextEdit):
                    val = editor.toPlainText()
                    if val == "{保留}":
                        continue
                    elif val == "":
                        continue
                    result['_fields']['base'][info_key] = editor.toPlainText()
                elif isinstance(editor, QSpinBox):
                    text = editor.text()
                    if text == "{保留}":
                        continue  # 跳過保留值
                    result['_fields']['base'][info_key] = str(editor.value())
                else:
                    val = editor.text()
                    if val == "{保留}":
                        continue
                    elif val == "":
                        continue
                    result['_fields']['base'][info_key] = val
        SignalBus.metadataUpdated.emit(result)
