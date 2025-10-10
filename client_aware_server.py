"""
Initialization Middleware Demo

This demonstrates FastMCP's new ability to intercept MCP initialization
requests through middleware, in addition to regular tool calls.

Depends on modifications to FastMCP:

  1. Edit pyproject.toml, as below
  2. Re-install dependencies: `uv sync --no-cache --reinstall`

```toml

# pyproject.toml

# Remove version specification from `fastmcp`
dependencies = [
    "fastmcp",
]

# Set fastmcp source to local branch
[tool.uv.sources]
# fastmcp = { path = "../fastmcp", editable = true }

# middleware-initialization is currently on 2.11.3
fastmcp = { git = "git+file:///Users/rmichael/Documents/Personal/Source/fastmcp/fastmcp", branch = "middleware-initialization" }
```

"""

import logging
from enum import Enum
from importlib.metadata import version
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
server = FastMCP(name="ClientAwareMiddlewareDemo", version=version("fastmcp-experiments"))


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
