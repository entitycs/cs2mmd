import os
from mermaid_class.core.parsing.generic_parsing import parse_type_declaration
from mermaid_class.renderers import RENDERERS
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser

# Pre-load the C# language
CS_LANGUAGE = Language(tscsharp.language())
parser = Parser(CS_LANGUAGE)

def generate_diagram_from_csharp(
    content: bytes,
    file_path: str | None = None,
    diagram_type: str = "classDiagram",
    include_interfaces: bool | None = True,
    include_abstracts: bool | None = True,
) -> str:

    code_bytes = content
    tree = parser.parse(code_bytes)
    root = tree.root_node

    mermaid = []

    if file_path:
        mermaid.append(f"%% File: {os.path.basename(file_path)}")

    renderer = RENDERERS.get(diagram_type)

    if not renderer:
        raise ValueError(f"Unknown diagram type: {diagram_type}")
    
    if renderer[1]:
        mermaid.append(renderer[1])

    def walk(node):
        if node.type in (
            "class_declaration",
            "interface_declaration",
            "struct_declaration",
            "record_declaration",
        ):
            type_desc = parse_type_declaration(node, code_bytes)
            if not type_desc:
                return

            if type_desc.is_interface and not include_interfaces:
                return
            if type_desc.is_abstract and not include_abstracts:
                return

            renderer[0](type_desc, mermaid)

        for child in node.children:
            walk(child)

    walk(root)

    return "\n".join(mermaid)
