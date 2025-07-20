from PySide6.QtWidgets import QApplication
import sys
# 自訂庫
from src.app.main_window import ComicInfoEditor
from src.core.controller import BackendCore
from src.app.app_sys_ctl import AppSysCtl

def main():
    # 後端初始化
    backendCore = BackendCore()

    # 應用控制初始化
    appSysCtl = AppSysCtl()

    # 應用執行
    appSysCtl.window.show()
    sys.exit(appSysCtl.application.exec())

if __name__ == "__main__":
    main()