import xml.etree.ElementTree as ET
import html
import re
def extract_text(raw):
    if raw is None:
        return None
    return html.unescape(ET.fromstring(f"<root>{raw}</root>").text or raw)
def remove_font_tags(text: str) -> str:
    """提取 <font> 标签中的纯文本内容。"""
    return re.sub(r"<font[^>]*>(.*?)</font>", r"\1", text, flags=re.IGNORECASE)
def parse_mxgraph_model(xml_str):
    root = ET.fromstring(xml_str)
    cells = root.findall(".//mxCell")

    id_to_node = {}
    children_map = {}

    for cell in cells:
        cell_id = cell.get("id")
        parent_id = cell.get("parent")
        value = extract_text(cell.get("value"))

        if cell.get("vertex") == "1":
            id_to_node[cell_id] = {
                "id": cell_id,
                "name": remove_font_tags(value) if value else "",
                "children": []
            }

        if parent_id:
            children_map.setdefault(parent_id, []).append(cell_id)

    # 构建递归结构
    def build_tree(cell_id):
        node = id_to_node.get(cell_id)
        if not node:
            return None
        for child_id in children_map.get(cell_id, []):
            child_node = build_tree(child_id)
            if child_node:
                node["children"].append(child_node)
        return node

    # 找顶层节点（无其他节点指向它为 parent）
    # 找顶层 vertex 节点：它的 parent 不是 vertex
    all_vertex_ids = set(id_to_node.keys())
    top_ids = []

    for cid, node in id_to_node.items():
        parent_id = next(  # 获取它在 children_map 中的父节点
            (pid for pid, children in children_map.items() if cid in children),
            None
        )
        if not parent_id or parent_id not in all_vertex_ids:
            top_ids.append(cid)

    def node_to_dict(node):
        if not node["children"]:
            return {node["name"]: ""}
        return {
            node["name"]: {
                k: v for child in node["children"]
                for k, v in node_to_dict(child).items()
            }
        }

    # 返回合并后的 JSON 结构
    result = {}
    for top_id in top_ids:
        tree = build_tree(top_id)
        if tree:
            result.update(node_to_dict(tree))
    return result

