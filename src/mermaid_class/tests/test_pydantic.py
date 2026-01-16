from fastapi.testclient import TestClient
from fastmcp.client import Client
from mermaid_class.fast_mcp_server.main import server
from mermaid_class.fast_api_server.main import app
import mermaid_class.core.parser as p
import inspect
import asyncio

print("Loaded from:", p.__file__)
print("Functions:", [name for name, _ in inspect.getmembers(p, inspect.isfunction)])
client = TestClient(app)
mcp_client = Client(server)

def test_generate_class_diagrams_dispatcher():

    print("openapi ROUTES:", [getattr(r, "path", None) for r in app.routes])
    tool_list = asyncio.run(server.get_tools())
    print("mcp ROUTES:", tool_list)
    payload = {
        "files": [{"content": "class foo()"}],
        # "knowledge": [],
        # "shell": [],
        "options": None
    }

    response = client.post("/code_doc/generate_mermaid_diagrams", json=payload)
    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200