from fastmcp import FastMCP

#
# FastMCP exceptions bug
#

# from fastmcp.exceptions import ResourceError, ToolError

# server = FastMCP("Exceptions")

#   @server.resource("boom://boom")
#   def boom_resource() -> None:
#       raise ResourceError

#   @server.tool()
#   def boom_tool() -> None:
#       raise ToolError



#
# Integer enum schema bug
#

from enum import Enum
from typing import Annotated
from pydantic import Field

class Amount(Enum):
    #   ONE=1
    #   TWO=2

    # String works:
    ONE="1"
    TWO="2"


# server = FastMCP("Enum schema")

#   @server.tool
#   def annotated_enum_tool(quantity: Annotated[Amount, Field(description="The quantity annotation.")]) -> str:
#       """An annotated quantity."""
#       return f"Received {quantity}"


#
# Empty server

#   Generates empty components objects; but not, for example `completions: {}`.
#
#   Spec language is the same.
#


server = FastMCP("Empty", version="1.2.3")

#   {
#     "capabilities": {
#       "experimental": {},
#       "prompts": {
#         "listChanged": false
#       },
#       "resources": {
#         "subscribe": false,
#         "listChanged": false
#       },
#       "tools": {
#         "listChanged": true
#       }
#     },
#     "serverInfo": {
#       "name": "Empty",
#       "version": "1.2.3"
#     }
#   }



def main():
    server.run()

if __name__ == "__main__":
    main()
