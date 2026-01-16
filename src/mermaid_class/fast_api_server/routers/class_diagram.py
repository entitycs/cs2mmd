from typing import List
from fastapi import APIRouter, HTTPException
from fastapi import Body
from pygres.db.database import Database
from mermaid_class.types import DEFAULT_DIAGRAM_TYPE
from mermaid_class.core.table_models import ClassDiagramTable, ClassDiagramRow
from mermaid_class.config.internal.internal_config import config
from mermaid_class.core import (
    VirtualFile,
    DiagramItem,
    DiagramRequest,
    BulkDiagramResponse,
    DiagramRequestOptions,
    process_bytes_response,
    process_path_response,
    normalize_path,
    logger
)

DEFAULT_PATH='/workspace/src'

router = APIRouter(prefix="/code_doc", tags=["mermaid", "classDiagram"])

@router.post("/generate_mermaid_diagrams", response_model=BulkDiagramResponse, operation_id="generate_mermaid_diagrams")
async def generate_mermaid_diagrams(request: DiagramRequest = Body(...)):
    """
    Generate Mermaid class diagrams from C# source files using a unified,
    multi‑source request model designed for LLM and agent consumption.

    This endpoint accepts **multiple forms of input**—real files, virtual files,
    inline overrides, shell output, and knowledge blobs—and merges them into a
    single analysis context. Agents should construct requests using the schemas
    below to ensure correct routing and diagram generation.

    ---------------------------------------------------------------------------
    HIGH‑LEVEL BEHAVIOR
    ---------------------------------------------------------------------------
    - The endpoint analyzes one or more `.cs` files and produces Mermaid class
      diagrams describing classes, interfaces, inheritance, and relationships.
    - Input may come from:
        * Virtual files (inline content or container paths)
    - The `options` field determines whether the request is:
        * If **interfaces**, or
        * If **abstract classes** should be included (default: true, for both)
    - The response always returns a `BulkDiagramResponse`, even for single‑file
      mode, to maintain a consistent schema.

    ---------------------------------------------------------------------------
    REQUEST SCHEMA (DiagramRequest)
    ---------------------------------------------------------------------------

    :param request: A DiagramRequest object containing the following fields:

    ---------------------------------------------------------------------------
    FILE SOURCES (request.files: list[VirtualFile] | required)
    ---------------------------------------------------------------------------
    A list of VirtualFile objects representing source files. Each VirtualFile
    must follow these rules:

        - content: str | None
            Inline file content. If provided, `path` MUST be None.
            Agents should use this when the file does not exist inside the
            container or when overriding the on‑disk version.

        - path: str | None
            Filesystem path to a `.cs` file inside the container.
            If provided, `content` MUST be None.
            Agents should only reference paths known to exist inside the
            execution environment.

        - language: str | None
            Optional language hint (e.g., "cs"). Defaults to "cs" if omitted.

    IMPORTANT:
        Agents cannot access the user's local filesystem.
        If a referenced `path` does not exist inside the container, the agent
        MUST provide the full file content in `content`.

    ---------------------------------------------------------------------------
    OPTION GROUPS (request.options: ContainerSourceOptions | Optional)
    ---------------------------------------------------------------------------
    Agents must choose based
    on user intent.

    1. Single‑File Mode (request.files: [VirtualFile])
        {
            "files": "<array with VirtualFile object(s) containing one path to a .cs file each>"
        }
        Behavior:
        - Only the specified file is analyzed.
        - Virtual files may override the on‑disk file if path were incorrectly provided alongside content.

    2. Batch Mode (request.files: [VirtualFile])
        {
            "files": "<array of VirtualFile(s) with 'path' field set, presumed to contain .cs files>",
        }

        Behavior:
        - Scans the folder or path for `.cs` files.
        - Generates diagrams for up to `max_files` files (see request.options).
        - Returns `truncated=True` if the limit is reached.

    ---------------------------------------------------------------------------
    RESPONSE SCHEMA (BulkDiagramResponse)
    ---------------------------------------------------------------------------

    :return: BulkDiagramResponse containing:
        - content: list[DiagramItem]
            Each DiagramItem includes:
                * file_path: str
                * diagram: str (Mermaid code)

        - processed: int
            Number of files successfully processed.

        - truncated: bool
            True if `max_files` limited the output.

        - total_scanned: int
            Total `.cs` files discovered before applying limits.

    :rtype: BulkDiagramResponse

    ---------------------------------------------------------------------------
    EXAMPLE REQUESTS
    ---------------------------------------------------------------------------

    1. Generate a mermaid class diagram for a Single file with inline content:
        {
            "files": [
                { "content": "public class A {}", "path": null }
            ],
            "options": null
        }

    2. Generate diagrams for /workspace/src/Assets; Batch create; Excluding interfaces:
        {
            "files": [
                {"path": "/workspace/src/Assets"},
                ["path": "/altworkspace/src/"},
            ],
            "options": {
                "include_interfaces": false
            }
        }

    3. Generate a mermaid class diagra for the file @/workspace/src/MyFile.cs.
        {
            "files": [
                { "path": "/workspace/src/MyFile.cs" }
            ]
        }
    """

    logger.info(request)
    db =  Database(
        host='postgresql',
        port=5432,
        dbname='classdiagram_request',
        user='mermaid',
        password=config.DB_PW,
        connect_timeout=10
    )
    diagram_type = "classDiagram"
    max_files = 10
    inc_interfaces = True
    inc_abstracts = True
    a_table = ClassDiagramTable(db)
    to_table = ClassDiagramRow(input=request)
    saved_to_table : ClassDiagramRow  = a_table.add(to_table)
    
    logger.debug("saved output: ", saved_to_table.output)

    diagrams : BulkDiagramResponse = BulkDiagramResponse(
        result = [],
        processed=0,
        truncated = False,
        total_scanned = 0
    )
    
    if request.files:
        for vn in request.files:

            bulkResponse : BulkDiagramResponse | None = None
            if request.options:
                if request.options.include_interfaces:
                    inc_interfaces = request.options.include_interfaces
                if  request.options.include_abstracts:
                    inc_abstracts = request.options.include_abstracts
                if request.options.max_files:
                    max_files = request.options.max_files
                if request.options.diagram_type:
                    diagram_type = request.options.diagram_type

            if vn.content:
                code_bytes = vn.content.encode("utf-8")

                bulkResponse = process_bytes_response(
                    [code_bytes],
                    diagram_type,
                    None,
                    include_interfaces = inc_interfaces,
                    include_abstracts = inc_abstracts,
                )
            elif vn.path:
                bulkResponse = bulk_generate_diagram(vn, DiagramRequestOptions(max_files=max_files, include_abstracts=inc_abstracts, include_interfaces=inc_interfaces))

            if bulkResponse:
                dlist : List[DiagramItem] = bulkResponse.result
                if dlist:
                    #or 
                    diagrams.result.extend(dlist)
                    #[diagrams.result.append(x) for x in dlist]

        return diagrams       

    # No valid option group provided
    raise HTTPException(status_code=400, detail="No valid diagram generation options provided.")

# @router.post("/bulk_class_diagram", response_model=BulkDiagramResponse, operation_id="get_class_diagrams_for_folder")
def bulk_generate_diagram(data: VirtualFile, options: DiagramRequestOptions):
    """
    Creates a list of Mermaid Class Diagrams given a folder path containing C# code.

    This endpoint serves as the FastAPI controller that orchestrates the bulk diagram generation process.
    It accepts a VirtualFile containing user configuration parameters.

    Key Features:
    - Processes multiple C# files recursively from a given folder path
    - Respects max_files limit to prevent excessive processing
    - Filters interfaces and abstract classes based on user preferences
    - Returns relative file paths and generated Mermaid diagrams as content
    - Provides metadata about processing status (processed count, truncation flag)

    :param data: Request object containing:
        - files: Path to folder containing .cs files (default: /workspace/src), or path to an individual .cs file
        - content: In place of files by path, the user may pass file content directly as a string
    :type data: VirtualFile

    :param options: Options object containing:
        - max_files: Maximum number of diagrams to generate (1-1000)
        - include_interfaces: Whether to include interface diagrams (default: True)
        - include_abstracts: Whether to include abstract class diagrams (default: True)
    :type options: DiagramRequestOptions

    :return: BulkDiagramResponse containing:
        - result: List of DiagramItem objects (file path + diagram)
        - processed: Number of files successfully processed
        - truncated: True if max_files limit was reached
        - total_scanned: Total .cs files found before applying limits
    :rtype: BulkDiagramResponse
    """
    _folder_path = data.path if data.path else DEFAULT_PATH
    _type = options.diagram_type if options.diagram_type else DEFAULT_DIAGRAM_TYPE
    return process_path_response(
        source_path=normalize_path(_folder_path),
        diagram_type=_type,
        max_diagrams=options.max_files,
        include_interfaces=options.include_interfaces,
        include_abstracts=options.include_abstracts,
    )
