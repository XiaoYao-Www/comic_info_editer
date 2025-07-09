from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
from .global_data_store import GlobalDataStore
from .classes import ClickableUrlLabel

class AppInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.store = GlobalDataStore()
        self.init_ui()

    def init_ui(self):
        """ 初始化UI元件 """
        layout = QVBoxLayout()

        # 作者資訊
        about_author_label = QLabel(self.tr("👻 作者資訊"))
        about_author_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        about_author_text = QTextEdit()
        about_author_text.setReadOnly(True)
        about_author_text.setPlainText(
            self.tr("逍遙 ( Xiao Yao )\n"
            "觀繁花而不與其爭艷\n"
            "處江湖而不染其煙塵")
        )
        layout.addWidget(about_author_label)
        layout.addWidget(about_author_text)

        # 軟體資訊
        about_software_label = QLabel(self.tr("📦 軟體資訊"))
        about_software_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        about_software_text = QTextEdit()
        about_software_text.setReadOnly(True)
        about_software_text.setPlainText(
            self.tr("版本: 0.1.0\n"
            "一款用於編輯漫畫 ComicInfo 的編輯器")
        )
        layout.addWidget(about_software_label)
        layout.addWidget(ClickableUrlLabel(self.tr("GitHub 專案連結"), "https://github.com/XiaoYao-Www/comic_info_editer"))
        layout.addWidget(about_software_text)

        # 加入主 Layout
        self.setLayout(layout)