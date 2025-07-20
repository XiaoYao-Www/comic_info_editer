from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
# 自訂庫
from src.classes.ui.clickable_url_label import ClickableUrlLabel
from src.setting import VERSION
from src.signal_bus import SIGNAL_BUS
## 翻譯
from src.translations import TR


class AppInfoTab(QWidget):
    """ 應用關於頁 """
    def __init__(self):
        super().__init__()
        # 初始化 UI
        self.init_ui()

        # 訊號連接
        self.signal_connection()

    ### 初始化函式 ###

    def init_ui(self):
        """ 初始化UI元件 """
        # 作者資訊
        ## 標籤
        self.about_author_label = QLabel(TR.UI_CONSTANTS["👻 作者資訊"]())
        self.about_author_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        ## 介紹內容
        self.about_author_text = QTextEdit()
        self.about_author_text.setPlainText(TR.UI_CONSTANTS["自我介紹"]())
        self.about_author_text.setReadOnly(True)
        ## github 連結
        self.about_author_github_label = ClickableUrlLabel(TR.UI_CONSTANTS["作者 Github 連結"](), "https://github.com/XiaoYao-Www")

        # 軟體資訊
        ## 標籤
        self.about_software_label = QLabel(TR.UI_CONSTANTS["📦 軟體資訊"]())
        self.about_software_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        ## 介紹內容
        self.about_software_text = QTextEdit()
        self.about_software_text.setPlainText(
            TR.UI_CONSTANTS["軟體介紹"]().format(version = VERSION)
        )
        self.about_software_text.setReadOnly(True)
        ## github 連結
        self.about_software_github_label = ClickableUrlLabel(TR.UI_CONSTANTS["GitHub 專案連結"](), "https://github.com/XiaoYao-Www/comic_info_editor")

        # 結構組合
        layout = QVBoxLayout()
        layout.addWidget(self.about_author_label)
        layout.addWidget(self.about_author_text)
        layout.addWidget(self.about_author_github_label)
        layout.addWidget(self.about_software_label)
        layout.addWidget(self.about_software_text)
        layout.addWidget(self.about_software_github_label)
        self.setLayout(layout)

    def signal_connection(self):
        """ 訊號連接 """
        # SIGNAL_BUS.ui.retranslateUi.connect(self.retranslateUi)
        pass

    ### 功能函式 ###

    def retranslateUi(self):
        """ UI 語言刷新 """
        self.about_author_label.setText(TR.UI_CONSTANTS["👻 作者資訊"]())
        self.about_author_text.setPlainText(TR.UI_CONSTANTS["自我介紹"]())
        self.about_author_github_label.setText(TR.UI_CONSTANTS["作者 Github 連結"]())
        #
        self.about_software_label.setText(TR.UI_CONSTANTS["📦 軟體資訊"]())
        self.about_software_text.setPlainText(
            TR.UI_CONSTANTS["軟體介紹"]().format(version = VERSION)
        )
        self.about_software_github_label.setText(TR.UI_CONSTANTS["GitHub 專案連結"]())
