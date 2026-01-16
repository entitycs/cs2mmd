from dataclasses import dataclass, field
from typing import List, Optional
from tree_sitter import Node

@dataclass
class MemberDescriptor:
    name: str
    type: str
    visibility: str
    kind: str  # "method" | "property" | "field"
    node: Node

@dataclass
class TypeDescriptor:
    typename: str
    is_interface: bool
    is_abstract: bool
    node: Node
    bases: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    members: List[MemberDescriptor] = field(default_factory=list)