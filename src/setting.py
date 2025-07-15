from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
# 自定庫
from src.classes.ui.smart_integer_field import SmartIntegerField

VERSION = "1.0.2"

schema_config = {
    "書籍資訊": {
        "Title": {
            "type": QLineEdit,
            "label": "標題",
            "info_key": "Title",
        },
        "Series": {
            "type": QLineEdit,
            "label": "系列名稱",
            "info_key": "Series",
        },
        "SeriesGroup": {
            "type": QLineEdit,
            "label": "系列分組",
            "info_key": "SeriesGroup",
        },
        "Genre": {
            "type": QLineEdit,
            "label": "風格類型",
            "info_key": "Genre",
        },
        "Number": {
            "type": QLineEdit,
            "label": "集數編號",
            "info_key": "Number",
        },
        "Count": {
            "type": SmartIntegerField,
            "label": "總集數",
            "info_key": "Count",
        },
        "Volume": {
            "type": SmartIntegerField,
            "label": "卷/冊號",
            "info_key": "Volume",
        },
        "PageCount": {
            "type": SmartIntegerField,
            "label": "頁數",
            "info_key": "PageCount",
        },
        "Format": {
            "type": QLineEdit,
            "label": "格式描述",
            "info_key": "Format",
        },
        "LanguageISO": {
            "type": QLineEdit,
            "label": "語言 (ISO 639)",
            "info_key": "LanguageISO",
        },
    },
    "替代版本": {
        "AlternateSeries": {
            "type": QLineEdit,
            "label": "替代系列名稱",
            "info_key": "AlternateSeries",
        },
        "AlternateNumber": {
            "type": QLineEdit,
            "label": "替代集數",
            "info_key": "AlternateNumber",
        },
        "AlternateCount": {
            "type": SmartIntegerField,
            "label": "替代總集數",
            "info_key": "AlternateCount",
        },
    },
    "內容摘要": {
        "Summary": {
            "type": QTextEdit,
            "label": "簡介",
            "info_key": "Summary",
        },
        "Notes": {
            "type": QTextEdit,
            "label": "備註",
            "info_key": "Notes",
        },
        "Review": {
            "type": QTextEdit,
            "label": "評論",
            "info_key": "Review",
        },
    },
    "角色與劇情": {
        "Characters": {
            "type": QLineEdit,
            "label": "登場角色",
            "info_key": "Characters",
        },
        "MainCharacterOrTeam": {
            "type": QLineEdit,
            "label": "主角或主團隊",
            "info_key": "MainCharacterOrTeam",
        },
        "StoryArc": {
            "type": QTextEdit,
            "label": "故事主軸",
            "info_key": "StoryArc",
        },
        "Locations": {
            "type": QLineEdit,
            "label": "地點",
            "info_key": "Locations",
        },
        "Teams": {
            "type": QLineEdit,
            "label": "出場團隊",
            "info_key": "Teams",
        },
    },
    "內容屬性": {
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
        "Manga": {
            "type": QComboBox,
            "label": "是否為漫畫",
            "info_key": "Manga",
            "options": [
                "",
                "{保留}",
                "Unknown",
                "Yes",
                "No",
                "YesAndRightToLeft",
            ],
        },
        "AgeRating": {
            "type": QComboBox,
            "label": "年齡分級",
            "info_key": "AgeRating",
            "options": [
                "",
                "{保留}",
                "Unknown",
                "Adults Only 18+",
                "Early Childhood",
                "Everyone",
                "Everyone 10+",
                "G",
                "Kids to Adults",
                "M",
                "MA15+",
                "Mature 17+",
                "PG",
                "R18+",
                "Rating Pending",
                "Teen",
                "X18+",

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
            "label": "畫者 (鉛筆)",
            "info_key": "Penciller",
        },
        "Inker": {
            "type": QLineEdit,
            "label": "墨線師",
            "info_key": "Inker",
        },
        "Colorist": {
            "type": QLineEdit,
            "label": "上色師",
            "info_key": "Colorist",
        },
        "Letterer": {
            "type": QLineEdit,
            "label": "字體設計",
            "info_key": "Letterer",
        },
        "CoverArtist": {
            "type": QLineEdit,
            "label": "封面設計",
            "info_key": "CoverArtist",
        },
        "Editor": {
            "type": QLineEdit,
            "label": "編輯",
            "info_key": "Editor",
        },
    },
    "出版資訊": {
        "Publisher": {
            "type": QLineEdit,
            "label": "出版社",
            "info_key": "Publisher",
        },
        "Imprint": {
            "type": QLineEdit,
            "label": "品牌 / 出版系列",
            "info_key": "Imprint",
        },
        "Web": {
            "type": QLineEdit,
            "label": "網站",
            "info_key": "Web",
        },
        "Year": {
            "type": SmartIntegerField,
            "label": "出版年",
            "info_key": "Year",
        },
        "Month": {
            "type": SmartIntegerField,
            "label": "出版月",
            "info_key": "Month",
        },
        "Day": {
            "type": SmartIntegerField,
            "label": "出版日",
            "info_key": "Day",
        },
        "ScanInformation": {
            "type": QLineEdit,
            "label": "掃描資訊",
            "info_key": "ScanInformation",
        },
    }
}
