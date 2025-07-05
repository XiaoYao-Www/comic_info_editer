import os
import zipfile
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from natsort import natsorted

# 產生 ComicInfo.xml
def build_comicinfo_xml(metadata: dict):
    root = ET.Element("ComicInfo")
    for key, val in metadata.items():
        ET.SubElement(root, key).text = val
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

# 從檔名抽標題
def extract_title_from_filename(file_name: str) -> str:
    name = os.path.splitext(file_name)[0]
    clean = name.replace("_", " ").replace("-", " ").replace(".", " ")
    clean = clean.replace("vol", "Vol").replace("第", "Vol")
    return clean.strip().title()

# 佔位符解析
def resolve_placeholders(template: str, rel_path: str, index: int) -> str:
    file_name = os.path.basename(rel_path)
    folder = os.path.dirname(rel_path)
    parent = os.path.basename(folder) if folder else ""
    name_no_ext, ext = os.path.splitext(file_name)
    title_clean = extract_title_from_filename(file_name)
    return template.format(
        fileName=name_no_ext,
        number=index,
        ext=ext,
        folder=folder,
        parent=parent,
        relPath=rel_path,
        titleFromName=title_clean,
    )

# 讀取 zip 裡的 ComicInfo.xml（如果有）
def read_comicinfo_xml(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            if 'ComicInfo.xml' in zf.namelist():
                data = zf.read('ComicInfo.xml')
                root = ET.fromstring(data)
                return {child.tag: child.text for child in root}
    except Exception:
        pass
    return {}

class ComicBatchEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComicInfo 批次建立工具 (PySide6)")

        self.source_dir = ""
        self.output_dir = ""
        self.file_list = []
        self.file_metadata_cache = {}  # 快取每個檔案原始 ComicInfo.xml 資料

        self.metadata = {
            "Title": "{titleFromName}",
            "Series": "{parent}",
            "Number": "{number}",
            "Year": ""
        }
        self.output_ext = ".cbz"

        self.updating_fields = False  # 防止欄位更新時互相觸發

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 來源資料夾選擇
        h1 = QHBoxLayout()
        self.source_btn = QPushButton("選擇漫畫資料夾")
        self.source_btn.clicked.connect(self.select_source_folder)
        self.source_label = QLabel("尚未選擇")
        h1.addWidget(self.source_btn)
        h1.addWidget(self.source_label)
        layout.addLayout(h1)

        # 檔案列表與拖曳排序
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 支援多選
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)  # 啟用拖曳排序
        self.list_widget.model().rowsMoved.connect(self.on_rows_moved)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # 智慧排序按鈕
        self.sort_btn = QPushButton("智慧自動排序")
        self.sort_btn.clicked.connect(self.auto_sort)
        layout.addWidget(self.sort_btn)

        # Metadata 編輯欄
        self.edits = {}
        for key in self.metadata:
            h = QHBoxLayout()
            h.addWidget(QLabel(key))
            le = QLineEdit(self.metadata[key])
            le.textChanged.connect(lambda val, k=key: self.update_metadata(k, val))
            self.edits[key] = le
            h.addWidget(le)
            layout.addLayout(h)

        # 佔位符提示
        self.placeholder_label = QLabel(
            "可用佔位符：{fileName}, {titleFromName}, {number}, {ext}, {folder}, {parent}, {relPath}\n"
            "多選時顯示 {保留} 表示保留原值")
        layout.addWidget(self.placeholder_label)

        # 輸出資料夾與副檔名
        h3 = QHBoxLayout()
        self.output_btn = QPushButton("選擇輸出資料夾")
        self.output_btn.clicked.connect(self.select_output_folder)
        self.output_label = QLabel("尚未選擇")
        self.ext_combo = QComboBox()
        self.ext_combo.addItems([".cbz", ".zip"])
        self.ext_combo.currentTextChanged.connect(self.update_ext)
        h3.addWidget(self.output_btn)
        h3.addWidget(self.output_label)
        h3.addWidget(QLabel("輸出副檔名"))
        h3.addWidget(self.ext_combo)
        layout.addLayout(h3)

        # 執行按鈕
        self.run_btn = QPushButton("開始處理")
        self.run_btn.clicked.connect(self.process_all)
        layout.addWidget(self.run_btn)

        self.setLayout(layout)
        self.resize(800, 650)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇漫畫資料夾")
        if folder:
            self.source_dir = folder
            self.source_label.setText(folder)
            self.load_file_list()

    def load_file_list(self):
        self.file_list.clear()
        self.file_metadata_cache.clear()
        self.list_widget.clear()
        for root, _, files in os.walk(self.source_dir):
            for f in files:
                if f.lower().endswith(".zip") or f.lower().endswith(".cbz"):
                    rel_path = os.path.relpath(os.path.join(root, f), self.source_dir)
                    self.file_list.append(rel_path)
                    full_path = os.path.join(self.source_dir, rel_path)
                    # 快取原有 ComicInfo.xml
                    self.file_metadata_cache[rel_path] = read_comicinfo_xml(full_path)
                    self.list_widget.addItem(rel_path)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder:
            self.output_dir = folder
            self.output_label.setText(folder)

    def update_ext(self, val):
        self.output_ext = val

    def update_metadata(self, key, val):
        if self.updating_fields:
            return
        self.metadata[key] = val

    def on_rows_moved(self, parent, start, end, destination, row):
        new_order = []
        for i in range(self.list_widget.count()):
            new_order.append(self.list_widget.item(i).text())
        self.file_list = new_order

    def on_selection_changed(self):
        selected = [item.text() for item in self.list_widget.selectedItems()]
        self.updating_fields = True
        try:
            if len(selected) == 0:
                # 無選擇，清空欄位
                for k in self.edits:
                    self.edits[k].setText("")
            elif len(selected) == 1:
                # 單選時讀取快取的 ComicInfo.xml 資料，填充欄位，沒有就用預設
                data = self.file_metadata_cache.get(selected[0], {})
                for k in self.edits:
                    val = data.get(k, self.metadata.get(k, ""))
                    self.edits[k].setText(val if val else "")
            else:
                # 多選時欄位全設成 {保留}
                for k in self.edits:
                    self.edits[k].setText("{保留}")
        finally:
            self.updating_fields = False

    def process_all(self):
        if not self.output_dir:
            QMessageBox.critical(self, "錯誤", "請選擇輸出資料夾")
            return
        if not self.source_dir:
            QMessageBox.critical(self, "錯誤", "請選擇漫畫資料夾")
            return
        if not self.file_list:
            QMessageBox.information(self, "提示", "沒有找到漫畫檔案")
            return

        selected_items = [item.text() for item in self.list_widget.selectedItems()]
        if not selected_items:
            QMessageBox.information(self, "提示", "請至少選擇一個檔案進行處理")
            return

        for idx, rel_path in enumerate(self.file_list, start=1):
            if rel_path not in selected_items:
                continue
            src_path = os.path.join(self.source_dir, rel_path)
            out_rel_path = os.path.splitext(rel_path)[0] + self.output_ext
            dst_path = os.path.join(self.output_dir, out_rel_path)
            dst_folder = os.path.dirname(dst_path)
            os.makedirs(dst_folder, exist_ok=True)

            # 讀原始 ComicInfo.xml（若有）
            orig_meta = self.file_metadata_cache.get(rel_path, {})

            # 準備寫入資料
            new_meta = {}
            for k, template in self.metadata.items():
                if template == "{保留}":
                    # 保留原值(如果有)，沒有就空字串
                    new_meta[k] = orig_meta.get(k, "")
                else:
                    new_meta[k] = resolve_placeholders(template, rel_path, idx)

            with zipfile.ZipFile(src_path, "r") as zin:
                with zipfile.ZipFile(dst_path, "w") as zout:
                    for item in zin.infolist():
                        with zin.open(item) as src:
                            fname = os.path.basename(item.filename)  # 只保留檔名
                            zout.writestr(fname, src.read())

                    xml_data = build_comicinfo_xml(new_meta)
                    zout.writestr("ComicInfo.xml", xml_data)

        QMessageBox.information(self, "完成", "所有漫畫處理完成！")

    def auto_sort(self):
        self.file_list = natsorted(self.file_list)
        self.list_widget.clear()
        for f in self.file_list:
            self.list_widget.addItem(f)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ComicBatchEditor()
    window.show()
    sys.exit(app.exec())
