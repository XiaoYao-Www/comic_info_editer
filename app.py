from PySide6.QtWidgets import QApplication
import sys
# 自訂庫
from src.app.main_window import ComicInfoEditor
from src.core.controller import BackendCore

def main():
    # 後端初始化
    backendCore = BackendCore()

    # 應用創建
    app = QApplication(sys.argv)
    window = ComicInfoEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()