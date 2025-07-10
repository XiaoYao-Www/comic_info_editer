import lxml.etree as ET
import os
import zipfile
from lxml.builder import ElementMaker

from lxml.etree import QName  # 用於強制指定前綴

def parse_comicinfo(xml_content: bytes) -> dict:
    """ 解析 ComicInfo XML """
    try:
        tree = ET.fromstring(xml_content)
    except Exception as e:
        return {}

    nsmap = tree.nsmap.copy() if tree.nsmap else {}
    data = {'_nsmap': nsmap, '_fields': {}, '_complex': {}}

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

        # 複合型元素
        if len(elem.attrib) > 0 or len(elem):
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

    return data

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

def resolve_placeholders(template: str, context: dict) -> str:
        """ 解析佔位符模板內容 """
        if not isinstance(template, str):
            return template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            template = template.replace(placeholder, str(value))
        return template

def update_comicinfo_data(context: dict, original: dict, updated: dict) -> dict:
        """
        將 get_metadata() 的資料更新回 parse_comicinfo() 的結果中
        僅針對 _fields/base 做更新
        """
        data = original.copy()
        # 預設值
        data.setdefault('_fields', {'base': {}})
        data.setdefault('_complex', {})
        data.setdefault('_nsmap', {})
        # 處理
        for prefix, fields in updated.get('_fields', {}).items():
            if prefix not in data['_fields']:
                data['_fields'][prefix] = {}
            for key, val in fields.items():
                data['_fields'][prefix][key] = resolve_placeholders(val, context)

        return data