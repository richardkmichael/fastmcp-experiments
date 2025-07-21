from fastmcp import FastMCP

# Works with PR# 1192
import fastmcp
fastmcp.settings.dereference_json_schemas = True

#
# Integer enum schema bug
#

from enum import Enum
from typing import Annotated
from pydantic import Field


class Amount(Enum):
    ONE=1
    TWO=2

    # String works:
    #   ONE="1"
    #   TWO="2"

server = FastMCP("Enum schema")

@server.tool
def annotated_enum_tool(quantity: Annotated[Amount, Field(description="The quantity annotation.")]) -> str:
    """An annotated quantity."""
    return f"Received {quantity}"

def main():
    server.run()

if __name__ == "__main__":
    main()
