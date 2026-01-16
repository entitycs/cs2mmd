# """
# title: Bulk Mermaid Class Diagrams
# author: EntityCS
# description: This tool creates Mermaid Class Diagrams from an existing csharp codebase.
# required_open_webui_version: 0.4.0
# requirements: fastapi, starlette, pydantic
# version: 0.0.2
# licence: MIT
# """
# import json
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from starlette.requests import Request
# from starlette.responses import StreamingResponse
# # from fastmcp import FastMCP
# # from fastmcp.server.openapi import RouteMap, MCPType
# from mermaid_class.fast_api_server.routers.class_diagram import router as class_diagram_api_route
# from fastapi_mcp import FastApiMCP
# from mermaid_class.core import logger

# app = FastAPI(
#     title="Mermaid Diagram API",
#     version="1.0.1",
#     description="Provides mermaid diagrams for C# class source code",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # DEFAULT_PATH='/workspace/src'

# # @app.middleware("http")
# # async def log_requests(request: Request, call_next):
# #     body = await request.body()
# #     logger.info(f"→ {request.method} {request.url}")
# #     logger.info(f"Headers: {dict(request.headers)}")
# #     logger.info(f"Body: {body.decode('utf-8', errors='replace') or ''}")

# #     response = await call_next(request)

# #     async def stream():
# #         async for chunk in response.body_iterator:
# #             yield chunk
# #         logger.info(f"← {response.status_code}")

# #     return StreamingResponse(
# #         stream(),
# #         status_code=response.status_code,
# #         headers=response.headers,
# #         media_type=response.media_type,
# #     )


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     body = await request.body()
#     logger.info(f"→ {request.method} {request.url}")
#     logger.info(f"Headers: {dict(request.headers)}")
#     logger.info(f"Body: {body.decode('utf-8', errors='replace') or ''}")

#     response = await call_next(request)

#     async def stream():
#         async for chunk in response.body_iterator:
#             yield chunk
#         logger.info(f"← {response.status_code}")

#     return StreamingResponse(
#         stream(),
#         status_code=response.status_code,
#         headers=response.headers,
#         media_type=response.media_type,
#     )

# #new w/ router
# app.include_router(class_diagram_api_route)

# # 1. Generate MCP server from your API
# # mcp = FastMCP.from_fastapi(app=app, name="Mermaid Diagram MCP Server")
# mcp = FastApiMCP(app, name="Mermai Diagram MCP Server")
# mcp.mount_http()  # Adds /mcp endpoint
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)

# #     logger.info("=== MCP MESSAGE RECEIVED ===")
# #     logger.info(json.dumps(message, indent=2))



# # ,
# #     route_maps=[
# #         # Add custom tags to all POST endpoints
# #         RouteMap(
# #             methods=["OPTIONS"],
# #             pattern=r"^/",
# #             mcp_type=MCPType.EXCLUDE,
# #         )
# #     ]                      
# # )

# # 2. Create the MCP's ASGI app
# # mcp_app = mcp.http_app(path='/mcp')

# # 3. Create a new FastAPI app that combines both sets of routes
# # combined_app = FastAPI(
# #     title="E-commerce API with MCP",
# #     routes=[
# #         *mcp_app.routes,  # MCP routes
# #         *app.routes,      # Original API routes
# #     ],
# #     lifespan=mcp_app.lifespan,
# # )
# # combined_app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
