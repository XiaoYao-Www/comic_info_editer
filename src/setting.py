from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
# 自定庫
from src.classes.ui.smart_integer_field import SmartIntegerField

schema_config = {
    "基本資訊": {
        "Title": {
            "type": QLineEdit,
            "label": "標題",
            "info_key": "Title",
        },
        "Series": {
            "type": QLineEdit,
            "label": "系列",
            "info_key": "Series",
        },
        "Number": {
            "type": QLineEdit,
            "label": "集號",
            "info_key": "Number",
        },
        "Count": {
            "type": SmartIntegerField,
            "label": "總集數",
            "info_key": "Count",
        },
        "Summary": {
            "type": QTextEdit,
            "label": "簡介",
            "info_key": "Summary",
        },
        "BlackAndWhite": {
            "type": QComboBox,
            "label": "黑白色彩",
            "info_key": "BlackAndWhite",
            "options": [
                "",
                "{保留}",
                "Unknown",
                "Yes",
                "No",
            ],
        },
    },
    "創作團隊": {
        "Writer": {
            "type": QLineEdit,
            "label": "作者",
            "info_key": "Writer",
        },
        "Penciller": {
            "type": QLineEdit,
            "label": "鉛筆稿",
            "info_key": "Penciller",
        },
        "Inker": {
            "type": QLineEdit,
            "label": "上墨者",
            "info_key": "Inker",
        },
    },
    "出版資訊": {
        "Publisher": {
            "type": QLineEdit,
            "label": "出版社",
            "info_key": "Publisher",
        },
        "Web": {
            "type": QLineEdit,
            "label": "網站",
            "info_key": "Web",
        },
    }
}
