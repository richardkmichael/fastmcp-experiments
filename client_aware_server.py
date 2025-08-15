"""
Initialization Middleware Demo

This demonstrates FastMCP's new ability to intercept MCP initialization
requests through middleware, in addition to regular tool calls.

Depends on modifications to FastMCP.
"""

import logging
from enum import Enum
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from dereference_for_claude_middleware import DereferenceForClaudeMiddleware

# Adjust the global logging; will affect both middlewares, so they write to the same file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="tmp/client_aware_server.log",
    filemode="a",
)

logger = logging.getLogger(__name__)


# Define enum for testing schema dereferencing
class Amount(Enum):
    ONE = 1
    TWO = 2


# Create server
server = FastMCP("ClientAwareMiddlewareDemo", version="1.0.0")


server.add_middleware(DereferenceForClaudeMiddleware())


@server.tool
def enum_tool(
    quantity: Annotated[Amount, Field(description="The quantity annotation.")],
) -> str:
    """An annotated quantity tool that uses enum with $ref schema."""
    return f"Received {quantity.value}"


def main():
    server.run()


if __name__ == "__main__":
    main()
