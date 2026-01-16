from pydantic import BaseModel, Field
from typing import List

class VirtualFile(BaseModel):
    """
    VirtualFile can be a string of text representing a file, a path to a directory of files, or the path to a single file.
    """
    content: str | None = Field(
        None,
        description="Inline file content. Use this parameter when a string representing code or context is given. This should include all blocks of code string in their entirety."
    )
    path: str | None = Field(
        None,
        description="Absolute or container-relative path. Required if content is not provided. Must be None if content is provided."
    )
    language: str | None = Field(
        None,
        description="Optional language hint (cs, py, json, etc.).  These may be described implicity, or explicitly via code block markers like ```cs."
    )

    model_config = {
        "extra": "forbid"
    }


class DiagramRequestOptions(BaseModel):
    """
    Format of Request Options (global)
    """
    diagram_type : str | None = Field(default="classDiagram", description="the type of mermaid diagram to create; default is classDiagram")
    max_files: int | None = Field(10, ge=1, le=1000)
    include_interfaces: bool | None = True # note - likely to deprecate
    include_abstracts: bool | None = True

class DiagramRequest(BaseModel):
    """
    A Diagram Request.  Used to generate Mermaid Class Diagrams.
    """
    files: List[VirtualFile] = Field(
        description="List of VirtualFile objects code file or folder paths."
    )

    options: DiagramRequestOptions | None = Field(
        None,
        description= "Global request options  (mode, flags, thresholds, includes/excludes, etc.)."
    )
    model_config = {
        "extra": "forbid"
    }

class DiagramItem(BaseModel):
    """
    Format of response to retrieve a single mermaid diagrams from a file given its file path or filename.
    """
    file: str = Field(..., description="Relative path or filename of the source file")
    diagram: str = Field(..., description="Mermaid Diagram code for type classDiagram")


class BulkDiagramResponse(BaseModel):
    """
    Format of response to retrieve one or more mermaid diagrams from source code given a path (file path or filename), or from the current workspace.
    """
    result: List[DiagramItem] = Field(..., description="List of processed mermaid diagrams")
    processed: int = Field(..., description="Number of files processed")
    truncated: bool = Field(False, description="True if stopped early due to max_files")
    total_scanned: int = Field(0, description="Total .cs files found before limit")
