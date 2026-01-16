
from typing import List, Optional
from tree_sitter import Node
from mermaid_class.core.data import MemberDescriptor, TypeDescriptor

def _get_text(node: Node, code_bytes: bytes) -> str:
    return code_bytes[node.start_byte : node.end_byte].decode("utf-8")

def _get_visibility(modifiers_node: Node | None, code_bytes: bytes) -> str:
    """
    Get Node Visibility (public, protected, private, internal)
    """
    if not modifiers_node:
        return "-"  # default private
    mods_text = _get_text(modifiers_node, code_bytes).strip()
    if "public" in mods_text:
        return "+"
    if "protected" in mods_text:
        return "#"
    if "internal" in mods_text:
        return "~"
    return "-"

def parse_type_declaration(node: Node, code_bytes:bytes) -> Optional[TypeDescriptor]:
    """
    Parse Type Declaration
    Returns Type Descriptor given a Class, Interface, Struct, or Record Node (or None)
    :rtype: TypeDescriptor | None
    """
    # Get name
    name_node = node.child_by_field_name("name")
    if not name_node:
        return
    
    typename = _get_text(name_node, code_bytes)

    # Get modifiers
    modifiers_node = node.child_by_field_name("modifiers")
    modifiers_text = _get_text(modifiers_node, code_bytes) if modifiers_node else ""

    # Get body
    body_node = node.child_by_field_name("body")

    # Get base classes/interfaces
    bases = []
    base_list = node.child_by_field_name("base_list")
    if base_list:
        for child in base_list.children:
            if child.type == "identifier_name":
                bases.append(_get_text(child, code_bytes))

    # Get attributes
    attributes = []
    for child in node.children:
        if child.type == "attribute_list":
            attr_text = _get_text(child, code_bytes).strip()
            attributes.append(attr_text[1:-1].strip())

    # Determine type kind and apply filters
    is_interface = node.type == "interface_declaration"
    is_abstract = "abstract" in modifiers_text

    desc = TypeDescriptor(
        typename=typename,
        is_interface=is_interface,
        is_abstract=is_abstract,
        node=node,
        bases=bases,
        attributes=attributes,
    )

    # parse members
    if body_node:
        desc.members = parse_members(body_node, code_bytes)
    
    return desc

def parse_members(body_node: Node, code_bytes: bytes) -> List[MemberDescriptor]:
    """
    Parse Declared Members from Body Node
    """
    members = []
    for child in body_node.children:
        if child.type in ("property_declaration", "method_declaration", "field_declaration"):
            m = parse_member(child, code_bytes)
            if m:
                members.append(m)
    return members

def parse_member(node: Node, code_bytes: bytes) -> Optional[MemberDescriptor]:
    # visibility
    modifiers = node.child_by_field_name("modifiers")
    visibility = _get_visibility(modifiers, code_bytes) if modifiers else "-"

    # determine kind + name + type
    if node.type == "property_declaration":
        kind = "property"
        name_node = node.child_by_field_name("name")
        type_node = node.child_by_field_name("type")

    elif node.type == "method_declaration":
        kind = "method"
        name_node = node.child_by_field_name("name")
        type_node = node.child_by_field_name("returns")

    elif node.type == "field_declaration":
        kind = "field"
        declarators = node.child_by_field_name("declarators")
        name_node = declarators.child_by_field_name("name") if declarators else None
        type_node = node.child_by_field_name("type")

    else:
        return None

    if not name_node:
        return None

    name = _get_text(name_node, code_bytes)
    type_text = _get_text(type_node, code_bytes).strip() if type_node else "?"

    return MemberDescriptor(
        name=name,
        type=type_text,
        visibility=visibility,
        kind=kind,
        node=node,
    )
 