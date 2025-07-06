from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
from .global_data_store import GlobalDataStore

class InfoEditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.store = GlobalDataStore()
        self.init_ui()

    def init_ui(self):
        """ 初始化UI元件 """
        layout = QVBoxLayout()

        # 加入主 Layout
        self.setLayout(layout)