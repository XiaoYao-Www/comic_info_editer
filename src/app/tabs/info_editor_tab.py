from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy,
    QToolButton
)
from PySide6.QtCore import Qt
# 自訂庫
from src.global_data_store import GLOBAL_DATA_STORE
from src.signal_bus import SIGNAL_BUS
from src.setting import schema_config
from src.classes.ui.smart_integer_field import SmartIntegerField
## 翻譯
from src.translations import TR

class InfoEditorTab(QWidget):
    def __init__(self):
        super().__init__()
        # 變數創建
        self.toggle_buttons = {}
        self.editors = {}
        self.labels = {}

        # 初始化 UI
        self.init_ui()

        # 訊號連接
        self.signal_connection()

        # 功能建構
        self.functional_construction()

    ### 初始化函式 ### 

    def init_ui(self):
        """ 初始化UI元件 """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for section_key, fields in schema_config.items():
            toggle_button = QToolButton(text=TR.SCHEMA_CONFIG[section_key](), checkable=True, checked=False)
            toggle_button.setStyleSheet("QToolButton { border: none; }")
            toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            toggle_button.setArrowType(Qt.RightArrow)
            self.toggle_buttons[section_key] = toggle_button

            content_area = QWidget()
            content_layout = QVBoxLayout()
            content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            content_area.setLayout(content_layout)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(content_area)
            scroll.setVisible(False)

            def make_toggle_func(button=toggle_button, area=scroll):
                return lambda checked: (button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow), area.setVisible(checked))

            toggle_button.toggled.connect(make_toggle_func())

            layout.addWidget(toggle_button)
            layout.addWidget(scroll)

            for field_key, field_cfg in fields.items():
                hlayout = QHBoxLayout()
                label = QLabel(TR.SCHEMA_CONFIG[field_cfg["label"]]())
                label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
                hlayout.addWidget(label, stretch=1)
                self.labels[field_cfg["info_key"]] = label

                widget_cls = field_cfg["type"]
                if widget_cls == QComboBox:
                    widget = QComboBox()
                    widget.addItems(field_cfg.get("options", ["{保留}"]))
                elif widget_cls == SmartIntegerField:
                    widget = SmartIntegerField()
                elif widget_cls == QTextEdit:
                    widget = QTextEdit()
                else:
                    widget = widget_cls()

                hlayout.addWidget(widget, stretch=7)
                content_layout.addLayout(hlayout)
                self.editors[field_cfg["info_key"]] = widget

        # 加入主 Layout
        self.setLayout(layout)

    def signal_connection(self):
        """ 訊號連結 """
        # 選擇後刷新
        SIGNAL_BUS.selectedComicPath.connect(self.set_data_list)
        # 請求輸入訊息
        SIGNAL_BUS.requireInfoEditorInput.connect(self.get_input_data)
        # 語言刷新
        # SIGNAL_BUS.ui.retranslateUi.connect(self.retranslateUi)

    def functional_construction(self):
        """ 功能建構 """
        pass

    ### 功能函式 ###

    def set_data_list(self, comic_paths: list[str]) -> None:
        """
        多筆資料設定：若欄位值一致就顯示該值，否則顯示 {保留}
        """
        all_comic_caches = GLOBAL_DATA_STORE.get("file_metadata_cache")
        selected_comic_caches = [all_comic_caches[filePath] for filePath in comic_paths]
        self.updating_fields = True
        try:
            for section, fields in schema_config.items():
                for field_key, field_cfg in fields.items():
                    info_key = field_cfg["info_key"]
                    values = []

                    for d in selected_comic_caches:
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
                            idx = editor.findText("{保留}")
                        editor.setCurrentIndex(idx)
                    elif isinstance(editor, QTextEdit):
                        editor.setPlainText(display_val)
                    elif isinstance(editor, SmartIntegerField):
                        if display_val == "{保留}" or display_val == "" or display_val == "-1":
                            editor.setValue(display_val)
                        else:
                            try:
                                editor.setValue(int(display_val))
                            except ValueError:
                                editor.setValue("{保留}")
                    else:
                        editor.setText(display_val)
        finally:
            self.updating_fields = False

    def get_input_data(self):
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
                    result['_fields']['base'][info_key] = editor.currentText()
                elif isinstance(editor, QTextEdit):
                    val = editor.toPlainText()
                    if val == "{保留}":
                        continue
                    result['_fields']['base'][info_key] = editor.toPlainText()
                elif isinstance(editor, SmartIntegerField):
                    value = editor.value()
                    if value == "{保留}" or value == "-1":
                        continue
                    result['_fields']['base'][info_key] = value
                else:
                    val = editor.text()
                    if val == "{保留}":
                        continue
                    result['_fields']['base'][info_key] = val
        SIGNAL_BUS.returnInfoEditorInput.emit(result)

    def retranslateUi(self):
        """ UI 語言刷新 """
        for section_key, fields in schema_config.items():
            toggle_button: QToolButton = self.toggle_buttons[section_key]
            toggle_button.setText(TR.SCHEMA_CONFIG[section_key]())

            for field_key, field_cfg in fields.items():
                label: QLabel = self.labels[field_cfg["info_key"]]
                label.setText(TR.SCHEMA_CONFIG[field_cfg["label"]]())
