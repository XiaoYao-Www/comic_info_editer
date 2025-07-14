from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
# 自訂庫
from src.classes.ui.clickable_url_label import ClickableUrlLabel
from src.setting import VERSION


class AppInfoTab(QWidget):
    """ 應用關於頁 """
    def __init__(self):
        super().__init__()
        # 初始化 UI
        self.init_ui()

    def init_ui(self):
        """ 初始化UI元件 """
        # 作者資訊
        ## 標籤
        about_author_label = QLabel(self.tr("👻 作者資訊"))
        about_author_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        ## 介紹內容
        about_author_text = QTextEdit()
        about_author_text.setPlainText(
            self.tr("逍遙 ( Xiao Yao )\n"
            "觀繁花而不與其爭艷\n"
            "處江湖而不染其煙塵")
        )
        about_author_text.setReadOnly(True)
        ## github 連結
        about_author_github_label = ClickableUrlLabel(self.tr("作者 Github 連結"), "https://github.com/XiaoYao-Www")

        # 軟體資訊
        ## 標籤
        about_software_label = QLabel(self.tr("📦 軟體資訊"))
        about_software_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        ## 介紹內容
        about_software_text = QTextEdit()
        about_software_text.setPlainText(
            self.tr("版本: {version}\n"
            "一款用於編輯漫畫 ComicInfo 的編輯器").format(version = VERSION)
        )
        about_software_text.setReadOnly(True)
        ## github 連結
        about_software_github_label = ClickableUrlLabel(self.tr("GitHub 專案連結"), "https://github.com/XiaoYao-Www/comic_info_editor")

        # 結構組合
        layout = QVBoxLayout()
        layout.addWidget(about_author_label)
        layout.addWidget(about_author_text)
        layout.addWidget(about_author_github_label)
        layout.addWidget(about_software_label)
        layout.addWidget(about_software_text)
        layout.addWidget(about_software_github_label)
        self.setLayout(layout)