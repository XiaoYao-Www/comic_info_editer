from PySide6.QtCore import QObject, Signal
import os
import zipfile
# 自訂庫
from src.global_data_store import GLOBAL_DATA_STORE
from src.signal_bus import SIGNAL_BUS
from src.function.comicinfo_process import parse_comicinfo, generate_comicinfo

class FileReadWrite(QObject):
    def __init__(self):
        super().__init__()
        # 訊號綁定
        SIGNAL_BUS.dataChange.sourceDirChanged.connect(self.read_comic_folder)
        ## 寫入檔案
        ### 原位置寫入
        SIGNAL_BUS.writeFile.inPlace.connect(self.write_comicinfo_in_place)
        SIGNAL_BUS.writeFile.flatten.connect(self.write_comicinfo_flatten)

    def read_comic_folder(self, path: str) -> None:
        """ 讀取漫畫資料夾 """
        source_dir = GLOBAL_DATA_STORE.get("source_dir")
        file_list = []
        file_metadata_cache = {}

        if not os.path.isdir(source_dir):
            return
        
        for root, _, files in os.walk(source_dir):
            for f in files:
                if f.lower().endswith((".zip", ".cbz")):
                    rel_path = os.path.relpath(os.path.join(root, f), source_dir)
                    file_list.append(rel_path)
                    full_path = os.path.join(source_dir, rel_path)
                    file_metadata_cache[rel_path] = self.read_comicinfo_xml(full_path) # 載入 metadata 快取

        GLOBAL_DATA_STORE.update({
            "file_list": file_list,
            "file_metadata_cache": file_metadata_cache 
        })

        SIGNAL_BUS.fileReadReady.emit()

    def read_comicinfo_xml(self, zip_path):
        """ 讀取 ComicInfo.xml """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                comicinfo_path = next(
                    (name for name in zf.namelist() if name.lower().endswith("comicinfo.xml")),
                    None
                )

                if not comicinfo_path:
                    return {}

                with zf.open(comicinfo_path) as f:
                    parsed = parse_comicinfo(f.read())
                    parsed["_original_path"] = comicinfo_path  # <--- 記錄原始 ComicInfo.xml 的路徑
                    return parsed

        except Exception as e:
            return {}
        
    def write_comicinfo_in_place(self, old_zip_path, new_zip_path, data: dict):
        """ 在原位置寫入 ComicInfo.xml """
        temp_zip_path = new_zip_path + ".tmp"

        try:
            with zipfile.ZipFile(old_zip_path, 'r') as zin, zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_STORED) as zout:
                original_path = data.get("_original_path", "ComicInfo.xml")
                comicinfo_written = False

                for item in zin.infolist():
                    if item.filename.lower().endswith("comicinfo.xml"):
                        if not comicinfo_written:
                            zout.writestr(original_path, generate_comicinfo(data))
                            comicinfo_written = True
                        # skip all ComicInfo.xml
                        continue

                    with zin.open(item) as f:
                        zout.writestr(item.filename, f.read())

                # 沒找到原來位置 → 新增 ComicInfo.xml 在根目錄
                if not comicinfo_written:
                    zout.writestr("ComicInfo.xml", generate_comicinfo(data))

            os.replace(temp_zip_path, new_zip_path)

        except Exception as e:
            print(f"❌ ComicInfo 寫入錯誤：{e}")
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

    def write_comicinfo_flatten(self, old_zip_path, new_zip_path, data: dict):
        """ 鋪平化寫入 ComicInfo.xml """
        temp_zip_path = new_zip_path + ".tmp"
        seen = set()

        try:
            with zipfile.ZipFile(old_zip_path, 'r') as zin, zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_STORED) as zout:
                for item in zin.infolist():
                    filename = os.path.basename(item.filename)

                    if filename.lower() == "comicinfo.xml":
                        continue  # 全部捨棄 ComicInfo.xml，待會重寫

                    if filename in seen:
                        continue  # 同名檔案 → 跳過
                    seen.add(filename)

                    with zin.open(item) as f:
                        zout.writestr(filename, f.read())

                zout.writestr("ComicInfo.xml", generate_comicinfo(data))

            os.replace(temp_zip_path, new_zip_path)

        except Exception as e:
            print(f"❌ ComicInfo 寫入錯誤：{e}")
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)