from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)

# schema_fields = {
#     "string": [
#         "Title", "Series", "Number", "Count", "Volume",
#         "AlternateSeries", "AlternateNumber", "AlternateCount",
#         "Summary", "Notes", "Year", "Month", "Writer", "Penciller",
#         "Inker", "Colorist", "Letterer", "CoverArtist", "Editor",
#         "Publisher", "Imprint", "Genre", "Web", "PageCount",
#         "LanguageISO", "Format", "BlackAndWhite", "Manga"
#     ],
#     "bool": [
#         "BlackAndWhite", "Manga"
#     ]
# }

schema_config = {
    "基本資訊": {
        "Title": {"type": QLineEdit, "label": "標題", "info_key": "Title"},
        "Series": {"type": QLineEdit, "label": "系列", "info_key": "Series"},
        "Number": {"type": QLineEdit, "label": "集數", "info_key": "Number"},
        "Count": {"type": QLineEdit, "label": "總集數", "info_key": "Count"},
        "Summary": {"type": QTextEdit, "label": "簡介", "info_key": "Summary"},
    },
    "創作團隊": {
        "Writer": {"type": QLineEdit, "label": "作者", "info_key": "Writer"},
        "Penciller": {"type": QLineEdit, "label": "鉛筆稿", "info_key": "Penciller"},
        "Inker": {"type": QLineEdit, "label": "上墨者", "info_key": "Inker"},
    },
    "出版資訊": {
        "Publisher": {"type": QLineEdit, "label": "出版社", "info_key": "Publisher"},
        "Web": {"type": QLineEdit, "label": "網站", "info_key": "Web"},
    }
}
