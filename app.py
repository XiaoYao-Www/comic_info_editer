from PySide6.QtWidgets import QApplication
from src.app.app_main import ComicInfoEditor

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ComicInfoEditor()
    window.show()
    sys.exit(app.exec())