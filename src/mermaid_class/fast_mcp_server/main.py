from typing import Any
from fastmcp.server.dependencies import get_http_headers, get_http_request
from fastmcp.server.middleware import Middleware
from fastmcp.server.middleware.middleware import CallNext, MiddlewareContext
import httpx
from fastmcp import FastMCP
from mcp.types import Request
from mermaid_class.core import logger

# ----------------------------------------------------------------------
# Server definition
# ----------------------------------------------------------------------
# Use the service name from docker-compose as hostname
client = httpx.AsyncClient(base_url="http://mermaid-openapi:8000")

# Load the OpenAPI spec synchronously once
openapi_spec = httpx.get("http://mermaid-openapi:8000/openapi.json").json()

# Create the MCP server
server = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="Mermaid MCP Server"
)
class MCPMiddleWare(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next: CallNext[Request[Any, Any], Any]) -> Any:

        # class SessionAwareMiddleware(Middleware):
    # async def on_request(self, context: MiddlewareContext, call_next):
        ctx = context.fastmcp_context
        

        if ctx and ctx.request_context:
            await ctx.info(f"→ {context.method} {context.source} {context.message}")
            # MCP session available - can access session-specific attributes
            # session_id = ctx.session_id
            request_id = ctx.request_id
            # await ctx.info(f"→ SESSION({session_id})")
            await ctx.info(f"→ REQUEST({request_id})")
        else:
            # MCP session not available yet - use HTTP helpers for request data (if using HTTP transport)
            headers = get_http_headers()
            request = get_http_request()
            # Access HTTP data for auth, logging, etc.
            logger.warning(f"→ HEADER: {headers}")
            logger.info(f"→ REQUEST: {request}")
        return await call_next(context)
        # return super().on_request(context, call_next)
    pass

server.add_middleware(MCPMiddleWare())

if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
