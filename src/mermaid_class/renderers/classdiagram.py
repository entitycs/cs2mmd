import re
from typing import List
from mermaid_class.core.data import MemberDescriptor, TypeDescriptor
# from mermaid_class.core.parsing import _strip_generics_local
def _strip_generics_local(name: str) -> str:
    return re.sub(r"<([^>]+)>", r"~\g<1>~", name.strip() if name else "")

render_header_classdiagram = "classDiagram\n"
def render_classdiagram(type_desc: TypeDescriptor, mermaid: List[str]):
    
    typename = _strip_generics_local(type_desc.typename)
    
    mermaid.append(f"class {typename}")

    has_body = False
    if type_desc.members and len(type_desc.members) > 0:
        has_body = True
    elif type_desc.is_interface or type_desc.is_abstract:
        has_body = True
    if has_body:
        mermaid.append(" {")

    if type_desc.is_interface:
        mermaid.append("    <<interface>>")
    elif type_desc.is_abstract:
        mermaid.append("    <<abstract>>")

    for member in type_desc.members:
        render_member_classdiagram(member, mermaid)

    if has_body:
        mermaid.append("}\n")

    # inheritance / implements
    for base in type_desc.bases:
        arrow = " <.. " if type_desc.is_interface else " <|-- "
        mermaid.append(f"{base}{arrow}{typename}")

    # attributes as notes
    for attr in type_desc.attributes:
        mermaid.append(f'note for {typename} "{attr}"')

def render_member_classdiagram(member: MemberDescriptor, mermaid: List[str]):
    vis = member.visibility
    name = member.name
    type_text = member.type

    if member.kind == "method":
        name += "()"  # TODO: ticket:FT:1

    mermaid.append(f"    {vis}{name} : {type_text}")
