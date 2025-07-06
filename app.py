import os
import zipfile
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit,
    QMessageBox, QComboBox, QAbstractItemView, QTabWidget,
    QTextEdit, QProgressBar, QSpinBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from natsort import natsorted

# ======= 工具函式(示範，請用你自己邏輯替換) =======
def read_comicinfo_xml(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            if "ComicInfo.xml" in z.namelist():
                with z.open("ComicInfo.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    return {elem.tag: elem.text for elem in root}
    except:
        pass
    return {}

def build_comicinfo_xml(data):
    SCHEMA_FIELDS = [
        "Title", "Series", "Number", "Count", "Volume",
        "AlternateSeries", "AlternateNumber", "AlternateCount",
        "Summary", "Notes", "Year", "Month", "Writer", "Penciller",
        "Inker", "Colorist", "Letterer", "CoverArtist", "Editor",
        "Publisher", "Imprint", "Genre", "Web", "PageCount",
        "LanguageISO", "Format", "BlackAndWhite", "Manga"
    ]
    root = ET.Element("ComicInfo")
    for key in SCHEMA_FIELDS:
        if key in data:
            val = data[key]
            if val is None or str(val).strip() == "":
                continue
            if key in {"Count", "Volume", "AlternateCount", "Year", "Month", "PageCount"}:
                try:
                    val = str(int(val))
                except:
                    continue
            elif key in {"BlackAndWhite", "Manga"}:
                if val not in {"Yes", "No", "Unknown"}:
                    val = "Unknown"
            ET.SubElement(root, key).text = val
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def resolve_placeholders(template, rel_path, index):
    folder = os.path.dirname(rel_path)
    fileName = os.path.basename(rel_path)
    name, ext = os.path.splitext(fileName)
    parent = os.path.basename(os.path.dirname(os.path.join("dummy", rel_path)))
    placeholders = {
        "{fileName}": fileName,
        "{titleFromName}": name,
        "{number}": str(index),
        "{ext}": ext,
        "{folder}": folder,
        "{parent}": parent,
        "{relPath}": rel_path,
    }
    for ph, val in placeholders.items():
        template = template.replace(ph, val)
    return template


class ComicInfoEditorTab(QWidget):
    # 編輯頁：顯示schema所有欄位的欄位編輯器（QLineEdit / QComboBox）
    # 多選時根據多個 dict 判斷是否顯示相同文字或 {保留}
    def __init__(self, schema_fields, yesno_fields, parent=None):
        super().__init__(parent)
        self.schema_fields = schema_fields
        self.yesno_fields = yesno_fields
        self.updating_fields = False
        self.current_data_list = []  # 多選時傳入的多筆 dict
        self.metadata = {}  # 編輯結果，key->value

        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        form_layout = QVBoxLayout()

        self.editors = {}

        for key in schema_fields:
            h = QHBoxLayout()
            label = QLabel(key)
            label.setFixedWidth(120)
            h.addWidget(label)

            if key in yesno_fields:
                combo = QComboBox()
                combo.addItems(["Unknown", "Yes", "No"])
                combo.currentTextChanged.connect(lambda val, k=key: self.on_field_changed(k, val))
                self.editors[key] = combo
                h.addWidget(combo)
            else:
                le = QLineEdit()
                le.textChanged.connect(lambda val, k=key: self.on_field_changed(k, val))
                self.editors[key] = le
                h.addWidget(le)

            form_layout.addLayout(h)

        container.setLayout(form_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def on_field_changed(self, key, val):
        if self.updating_fields:
            return
        self.metadata[key] = val

    def set_data_list(self, data_list):
        # 多筆資料設定，顯示相同值或{保留}
        self.current_data_list = data_list
        self.updating_fields = True
        try:
            for key in self.schema_fields:
                values = [d.get(key, "") for d in data_list if d]
                if not values:
                    text = ""
                elif all(v == values[0] for v in values):
                    text = values[0]
                else:
                    text = "{保留}"

                editor = self.editors.get(key)
                if isinstance(editor, QComboBox):
                    # ComboBox 預設值設為 Unknown 可接受任何值
                    idx = editor.findText(text)
                    if idx == -1:
                        idx = editor.findText("Unknown")
                    editor.setCurrentIndex(idx)
                else:
                    editor.setText(text)
                self.metadata[key] = text
        finally:
            self.updating_fields = False


class ComicBatchEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComicInfo 批次建立工具")

        self.source_dir = ""
        self.output_dir = ""
        self.file_list = []
        self.file_metadata_cache = {}

        # 預設部分欄位值
        self.metadata = {
            "Title": "{titleFromName}",
            "Series": "{parent}",
            "Number": "{number}",
            "Year": ""
        }
        self.output_ext = ".cbz"
        self.updating_fields = False

        self.schema_fields = [
            "Title", "Series", "Number", "Count", "Volume",
            "AlternateSeries", "AlternateNumber", "AlternateCount",
            "Summary", "Notes", "Year", "Month", "Writer", "Penciller",
            "Inker", "Colorist", "Letterer", "CoverArtist", "Editor",
            "Publisher", "Imprint", "Genre", "Web", "PageCount",
            "LanguageISO", "Format", "BlackAndWhite", "Manga"
        ]
        self.yesno_fields = {"BlackAndWhite", "Manga"}

        self.setup_ui()

    def setup_ui(self):
        self.tabs = QTabWidget()

        # 批次處理分頁
        main_tab = QWidget()
        main_layout = QVBoxLayout()

        # 來源資料夾選擇
        h1 = QHBoxLayout()
        self.source_btn = QPushButton("選擇漫畫資料夾")
        self.source_btn.clicked.connect(self.select_source_folder)
        self.source_label = QLabel("尚未選擇")
        h1.addWidget(self.source_btn)
        h1.addWidget(self.source_label)
        main_layout.addLayout(h1)

        # 排序選擇
        h_sort = QHBoxLayout()
        self.meta_sort_combo = QComboBox()
        self.meta_sort_combo.addItem("（依檔名排序）")
        self.meta_sort_combo.addItems(self.schema_fields)
        self.meta_sort_combo.currentTextChanged.connect(self.meta_sort)
        h_sort.addWidget(QLabel("排序依據："))
        h_sort.addWidget(self.meta_sort_combo)
        main_layout.addLayout(h_sort)

        # 檔案列表與拖曳排序
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.model().rowsMoved.connect(self.on_rows_moved)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.list_widget)

        self.selection_status = QLabel("已選中 0 / 共 0 本漫畫")
        main_layout.addWidget(self.selection_status)

        # 智慧排序按鈕
        self.sort_btn = QPushButton("智慧自動排序")
        self.sort_btn.clicked.connect(self.auto_sort)
        main_layout.addWidget(self.sort_btn)

        # 輸出選擇
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
        main_layout.addLayout(h3)

        self.run_btn = QPushButton("開始處理")
        self.run_btn.clicked.connect(self.process_all)
        main_layout.addWidget(self.run_btn)

        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        main_tab.setLayout(main_layout)
        self.tabs.addTab(main_tab, "📂 批次處理")

        # 作者資訊分頁
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        about_label = QLabel("🧑‍💻 作者資訊")
        about_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setPlainText(
            "ComicInfo 批次建立工具\n"
            "作者：OwO\n"
            "用途：批量添加 ComicInfo.xml，並保留原始資料結構與排序"
        )
        about_layout.addWidget(about_label)
        about_layout.addWidget(about_text)
        about_tab.setLayout(about_layout)
        self.tabs.addTab(about_tab, "👤 作者資訊")

        # ComicInfo 編輯分頁 (全部欄位)
        self.comicinfo_editor = ComicInfoEditorTab(self.schema_fields, self.yesno_fields)
        self.tabs.addTab(self.comicinfo_editor, "✏️ 編輯 ComicInfo")

        # 設定分頁
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        font_label = QLabel("字體大小")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 30)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        settings_layout.addWidget(font_label)
        settings_layout.addWidget(self.font_size_spin)
        settings_layout.addStretch()
        settings_tab.setLayout(settings_layout)
        self.tabs.addTab(settings_tab, "⚙️ 設定")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.resize(900, 750)

    def change_font_size(self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇漫畫資料夾")
        if folder:
            self.source_dir = folder
            self.source_label.setText(folder)
            self.load_file_list()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder:
            self.output_dir = folder
            self.output_label.setText(folder)

    def update_ext(self, val):
        self.output_ext = val

    def load_file_list(self):
        self.file_list.clear()
        self.file_metadata_cache.clear()
        self.list_widget.clear()
        for root, _, files in os.walk(self.source_dir):
            for f in files:
                if f.lower().endswith((".zip", ".cbz")):
                    rel_path = os.path.relpath(os.path.join(root, f), self.source_dir)
                    self.file_list.append(rel_path)
                    full_path = os.path.join(self.source_dir, rel_path)
                    self.file_metadata_cache[rel_path] = read_comicinfo_xml(full_path)
                    self.list_widget.addItem(rel_path)
        self.selection_status.setText(f"已選中 0 / 共 {len(self.file_list)} 本漫畫")

    def on_rows_moved(self, parent, start, end, destination, row):
        self.file_list = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]

    def on_selection_changed(self):
        selected = [item.text() for item in self.list_widget.selectedItems()]
        self.selection_status.setText(f"已選中 {len(selected)} / 共 {len(self.file_list)} 本漫畫")

        # 多選資料送編輯器
        all_data = [self.file_metadata_cache.get(path, {}) for path in selected] if selected else []
        self.comicinfo_editor.set_data_list(all_data)

        # 同步更新批次用 metadata (取編輯器當前值)
        # 由於編輯器更新自己metadata，這邊同步更新
        self.metadata.update(self.comicinfo_editor.metadata)

    def process_all(self):
        selected_items = [item.text() for item in self.list_widget.selectedItems()]
        if not self.output_dir:
            QMessageBox.critical(self, "錯誤", "請選擇輸出資料夾")
            return
        if not self.source_dir:
            QMessageBox.critical(self, "錯誤", "請選擇漫畫資料夾")
            return
        if not selected_items:
            QMessageBox.information(self, "提示", "請至少選擇一個檔案進行處理")
            return

        # 取最新編輯區 metadata 當輸出用
        batch_meta = self.comicinfo_editor.metadata

        self.progress_bar.setMaximum(len(selected_items))
        self.progress_bar.setValue(0)

        for idx, rel_path in enumerate(self.file_list, start=1):
            if rel_path not in selected_items:
                continue
            src_path = os.path.join(self.source_dir, rel_path)
            out_rel_path = os.path.splitext(rel_path)[0] + self.output_ext
            dst_path = os.path.join(self.output_dir, out_rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            orig_meta = self.file_metadata_cache.get(rel_path, {})

            new_meta = {}
            for k, template in batch_meta.items():
                if template == "{保留}":
                    new_meta[k] = orig_meta.get(k, "")
                else:
                    new_meta[k] = resolve_placeholders(template, rel_path, idx)

            with zipfile.ZipFile(src_path, "r") as zin:
                with zipfile.ZipFile(dst_path, "w") as zout:
                    for item in zin.infolist():
                        with zin.open(item) as src:
                            fname = os.path.basename(item.filename)
                            zout.writestr(fname, src.read())
                    xml_data = build_comicinfo_xml(new_meta)
                    zout.writestr("ComicInfo.xml", xml_data)

            self.progress_bar.setValue(self.progress_bar.value() + 1)
            QApplication.processEvents()

        QMessageBox.information(self, "完成", "所有漫畫處理完成！")

    def auto_sort(self):
        self.file_list = natsorted(self.file_list)
        self.list_widget.clear()
        for f in self.file_list:
            self.list_widget.addItem(f)

    def meta_sort(self, key):
        if key == "（依檔名排序）":
            self.file_list = natsorted(self.file_list)
        else:
            def get_meta_val(path):
                meta = self.file_metadata_cache.get(path, {})
                val = meta.get(key, "")
                return val if val is not None else ""
            self.file_list.sort(key=get_meta_val)
        self.list_widget.clear()
        for f in self.file_list:
            self.list_widget.addItem(f)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ComicBatchEditor()
    window.show()
    sys.exit(app.exec())
