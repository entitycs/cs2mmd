"""
title: Bulk Mermaid Class Diagrams
author: EntityCS
description: This tool creates Mermaid Class Diagrams from an existing csharp codebase.
required_open_webui_version: 0.4.0
requirements: fastapi, starlette, pydantic
version: 0.0.3
licence: MIT
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mermaid_class.fast_api_server.routers.class_diagram import router as class_diagram_api_route

app = FastAPI(
    title="Mermaid Diagram API",
    version="1.0.0",
    description="Provides mermaid diagrams for C# class source code",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(class_diagram_api_route)
