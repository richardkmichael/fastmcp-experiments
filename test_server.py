import pytest

from fastmcp import Client
from fastmcp.exceptions import ToolError

# from fastmcp.exceptions import ResourceError
from fastmcp.exceptions import McpError

import main

@pytest.fixture
def server():
    return main.server

@pytest.mark.asyncio
async def test_boom_tool(server):
    async with Client(server) as client:
        with pytest.raises(ToolError):
            await client.call_tool("boom_tool")

@pytest.mark.asyncio
async def test_boom_resource(server):
    async with Client(server) as client:
        # with pytest.raises(ResourceError):
        with pytest.raises(McpError):
            await client.read_resource("boom:://boom")
