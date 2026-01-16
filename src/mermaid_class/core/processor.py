# core/processor.py
import os
import pathlib
from typing import List

from mermaid_class.core.models import DiagramItem, BulkDiagramResponse
from mermaid_class.core.parser import generate_diagram_from_csharp
from mermaid_class.core.utils import logger
from mermaid_class.filetypes import FILETYPES as SUPPORTED_FILETYPES


def process_bytes_response(
    code_byte_list: list[bytes],
    diagram_type: str,
    filename: str | None = None,
    include_interfaces: bool | None = True,
    include_abstracts: bool | None = True,
) -> BulkDiagramResponse:
    diagrams: List[DiagramItem] = []
    for code_bytes in code_byte_list:
        raw_diagram = generate_diagram_from_csharp(
            content=code_bytes,
            file_path=filename if filename else None,
            diagram_type=diagram_type,
            include_interfaces=include_interfaces,
            include_abstracts=include_abstracts,
        )
        diagrams.append(
            DiagramItem(
                file=filename if filename else "from context", diagram=raw_diagram
            )
        )

    return BulkDiagramResponse(
        result=diagrams,
        processed=1,
        truncated=False,
        total_scanned=1,
    )


def process_path_response(
    source_path: pathlib.Path,
    diagram_type: str,
    max_diagrams: int | None,
    include_interfaces: bool | None,
    include_abstracts: bool | None,
) -> BulkDiagramResponse:
    """
    Shared bulk processing logic.
    Used by both FastAPI and MCP servers.
    """
    diagrams: List[DiagramItem] = []
    processed = 0
    total_scanned = 0
    path_str = str(source_path)
    _max_diagrams = max_diagrams if max_diagrams else 10

    def process_file(filepath_str: str, diagram_type: str):
        if not any(filepath_str.endswith(ext) for ext in SUPPORTED_FILETYPES):
            raise ValueError(f"Filetype not supported: {source_path}")
        try:
            if not os.path.isfile(filepath_str):
                raise ValueError(f"Not a file: {source_path}")
            try:
                with open(filepath_str, "r", encoding="utf-8") as f:
                    source_file = f.read()
            except Exception as e:
                raise RuntimeError(f"Cannot read file: {e}")

            code_bytes = source_file.encode("utf-8")

            raw_diagram = generate_diagram_from_csharp(
                code_bytes,
                filepath_str,
                diagram_type=diagram_type,
                include_interfaces=include_interfaces,
                include_abstracts=include_abstracts,
            )
            diagrams.append(DiagramItem(file=filepath_str, diagram=raw_diagram))

        except (ValueError, RuntimeError) as exc:
            raise ValueError(f"File or folder not readable: {filepath_str} - {exc}")
        pass

    if not source_path.exists():
        raise ValueError(f"File or Folder not found: {source_path}")
    if not source_path.is_dir():
        if source_path.is_file():
            process_file(path_str, diagram_type)
            total_scanned = 1

    for root, _, files in os.walk(source_path):
        total_scanned += 1
        for file in sorted(files):
            if (
                file.endswith(".cs")
                and not file.endswith(".g.cs")
                and "obj" not in root.split(os.sep)
            ):
                processed += 1
                full_path = pathlib.Path(root) / file
                try:
                    process_file(str(full_path), diagram_type)
                except (ValueError, RuntimeError) as exc:
                    logger.warning(f"Skipping {full_path}: {exc}")
                    continue

                if len(diagrams) >= _max_diagrams:
                    break
        if processed >= _max_diagrams:
            break

    return BulkDiagramResponse(
        result=diagrams,
        processed=processed,
        truncated=processed >= _max_diagrams,
        total_scanned=total_scanned,
    )
