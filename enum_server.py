# Works with PR# 1192
#   import fastmcp
#   fastmcp.settings.dereference_json_schemas = True
#
# Integer enum schema bug
#
from enum import Enum
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field


class Quantity(Enum):
    # Works with dereferenced schema
    ONE = 1
    TWO = 2

    # String works:
    #   ONE="1"
    #   TWO="2"


server = FastMCP("Enum schema")


@server.tool
def annotated_enum_tool(
    quantity: Annotated[Quantity, Field(description="The quantity annotation.")],
) -> str:
    """An annotated quantity."""
    return f"Received {quantity}"


def main():
    server.run()


if __name__ == "__main__":
    main()

# Enum dereferenced with patch
# =====================
#   {
#     "tools": [
#       {
#         "name": "annotated_enum_tool",
#         "description": "An annotated quantity.",
#         "inputSchema": {
#           "type": "object",
#           "properties": {
#             "quantity": {
#               "enum": [
#                 1,
#                 2
#               ],
#               "title": "Quantity",
#               "type": "integer",
#               "description": "The quantity annotation."
#             }
#           },
#           "required": [
#             "quantity"
#           ],
#           "$defs": {
#             "Amount": {
#               "enum": [
#                 1,
#                 2
#               ],
#               "title": "Amount",
#               "type": "integer"
#             }
#           }
#         },
#         "outputSchema": {
#           "type": "object",
#           "properties": {
#             "result": {
#               "title": "Result",
#               "type": "string"
#             }
#           },
#           "required": [
#             "result"
#           ],
#           "title": "_WrappedResult",
#           "x-fastmcp-wrap-result": true
#         }
#       }
#     ]
#   }



# Enum as integers
# =====================
#
#   {
#     "tools": [
#       {
#         "name": "annotated_enum_tool",
#         "description": "An annotated quantity.",
#         "inputSchema": {
#           "type": "object",
#           "properties": {
#             "quantity": {
#               "$ref": "#/$defs/Quantity",
#               "description": "The quantity annotation.",
#               "title": "Quantity"
#             }
#           },
#           "required": [
#             "quantity"
#           ],
#           "$defs": {
#             "Quantity": {
#               "enum": [
#                 1,
#                 2
#               ],
#               "title": "Quantity",
#               "type": "integer"
#             }
#           }
#         },
#         "outputSchema": {
#           "type": "object",
#           "properties": {
#             "result": {
#               "title": "Result",
#               "type": "string"
#             }
#           },
#           "required": [
#             "result"
#           ],
#           "title": "_WrappedResult",
#           "x-fastmcp-wrap-result": true
#         },
#         "_meta": {
#           "_fastmcp": {
#             "tags": []
#           }
#         }
#       }
#     ]
#   }
