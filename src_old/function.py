import lxml.etree as ET
import os
import zipfile
from lxml.builder import ElementMaker

from lxml.etree import QName  # 用於強制指定前綴

def generate_comicinfo(data: dict) -> bytes:
    """ 將資料轉換為 ComicInfo XML 格式（強制保留 prefix） """
    nsmap = data.get('_nsmap', {})
    
    # 根元素保留所有 namespace 宣告
    root = ET.Element("ComicInfo", nsmap=nsmap)

    # 處理單值欄位
    for prefix, fields in data.get('_fields', {}).items():
        for tag, value in fields.items():
            if not value.strip():
                continue  # 忽略空白字串

            if prefix == 'base':
                # base prefix 無 namespace，直接新增子元素
                el = ET.SubElement(root, tag)
                el.text = value
            else:
                # 強制使用指定前綴（即使 namespace URI 相同）
                namespace_uri = nsmap[prefix]
                qname = QName(namespace_uri, tag)  # 建立帶前綴的 QName
                el = ET.SubElement(root, qname.text, nsmap={prefix: namespace_uri})
                el.text = value

    # 處理複合欄位（有屬性和子元素）
    for prefix, groups in data.get('_complex', {}).items():
        for tag, entries in groups.items():
            for entry in entries:
                if prefix == 'base':
                    el = ET.SubElement(root, tag, attrib=entry['_attrs'])
                else:
                    namespace_uri = nsmap[prefix]
                    qname = QName(namespace_uri, tag)
                    el = ET.SubElement(root, qname.text, attrib=entry['_attrs'], nsmap={prefix: namespace_uri})

                for child in entry['_children']:
                    child_tag = child['tag']
                    child_attrib = child['attrib']
                    child_text = child['text']
                    child_el = ET.SubElement(el, child_tag, attrib=child_attrib)
                    child_el.text = child_text

    return ET.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)


def parse_comicinfo(xml_content: bytes) -> dict:
    """ 解析 ComicInfo XML """
    try:
        tree = ET.fromstring(xml_content)
    except Exception as e:
        # print(f"❌ ComicInfo 解析失敗: {e}")
        # print(xml_content.decode("utf-8", errors="replace"))
        return {}

    nsmap = tree.nsmap.copy() if tree.nsmap else {}
    data = {'_nsmap': nsmap, '_fields': {}, '_complex': {}}

    # print(f"[DEBUG] Root tag: {tree.tag}")
    # print(f"[DEBUG] Namespace map: {nsmap}")

    # 額外補漏 prefix → URI（在 XML 內部宣告，但 root 沒宣告的）
    for elem in tree.iter():
        prefix = elem.prefix
        namespace_uri = ET.QName(elem).namespace

        if prefix and namespace_uri and prefix not in data['_nsmap']:
            data['_nsmap'][prefix] = namespace_uri

    for elem in tree.iterchildren():
        prefix = elem.prefix or 'base'
        tag = ET.QName(elem).localname
        text = elem.text.strip() if elem.text else ''
        # print(f"[DEBUG] Element: prefix={prefix}, tag={tag}, text={text}")

        # 複合型元素
        if len(elem.attrib) > 0 or len(elem):
            # print(f"[DEBUG] → 是複合元素: attrib={elem.attrib}, 子元素數量={len(elem)}")
            if prefix not in data['_complex']:
                data['_complex'][prefix] = {}
            if tag not in data['_complex'][prefix]:
                data['_complex'][prefix][tag] = []

            entry = {'_attrs': dict(elem.attrib), '_children': []}
            for child in elem:
                child_tag = ET.QName(child).localname
                child_entry = {
                    'tag': child_tag,
                    'text': child.text.strip() if child.text else '',
                    'attrib': dict(child.attrib)
                }
                entry['_children'].append(child_entry)

            data['_complex'][prefix][tag].append(entry)
        else:
            if prefix not in data['_fields']:
                data['_fields'][prefix] = {}
            data['_fields'][prefix][tag] = text

    # print("[DEBUG] 解析完成結果:", data)
    return data


def read_comicinfo_xml(zip_path):
    """ 讀取 ComicInfo.xml """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            comicinfo_path = next(
                (name for name in zf.namelist() if name.lower().endswith("comicinfo.xml")),
                None
            )

            if not comicinfo_path:
                # print(f"[WARN] ComicInfo.xml 不存在於 {zip_path}")
                return {}

            with zf.open(comicinfo_path) as f:
                parsed = parse_comicinfo(f.read())
                parsed["_original_path"] = comicinfo_path  # <--- 記錄原始 ComicInfo.xml 的路徑
                return parsed

    except Exception as e:
        # print(f"❌ 讀取 ComicInfo.xml 失敗 ({zip_path}): {e}")
        return {}


def write_comicinfo_in_place(old_zip_path, new_zip_path, data: dict):
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
        # print(f"❌ 寫入 ComicInfo.xml 失敗: {e}")
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)

def write_comicinfo_flatten(old_zip_path, new_zip_path, data: dict):
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
        # print(f"❌ 重整 ComicInfo.xml 寫入失敗: {e}")
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
