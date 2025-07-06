import xml.etree.ElementTree as ET
import os
import zipfile

###
# 構建ComicInfo.xml
###
def build_comicinfo_xml(metadata: dict) -> str:
    root = ET.Element("ComicInfo")
    for key, val in metadata.items():
        ET.SubElement(root, key).text = val
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

###
# 從檔名抽標題
###
def extract_title_from_filename(file_name: str) -> str:
    name = os.path.splitext(file_name)[0]
    clean = name.replace("_", " ").replace("-", " ").replace(".", " ")
    clean = clean.replace("vol", "Vol").replace("第", "Vol")
    return clean.strip().title()

###
# 解析佔位符
###
def resolve_placeholders(template: str, rel_path: str, index: int) -> str:
    file_name = os.path.basename(rel_path)
    folder = os.path.dirname(rel_path)
    parent = os.path.basename(folder) if folder else ""
    name_no_ext, ext = os.path.splitext(file_name)
    title_clean = extract_title_from_filename(file_name)
    return template.format(
        fileName=name_no_ext, # 檔名
        number=index, # 編號
        ext=ext, # 副檔名
        parent=parent, # 父資料夾名稱
        titleFromName=title_clean, # 從檔名解析的標題
    )

###
# 讀取ComicInfo.xml
###
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