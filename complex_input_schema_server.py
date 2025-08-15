import logging
import os
from typing import Annotated, Any, TypedDict

from fastmcp import FastMCP
from pydantic import Field

from dereference_for_claude_middleware import DereferenceForClaudeMiddleware


def setup_logging():
    os.makedirs("tmp", exist_ok=True)

    # Adjust the global logging; will affect both middlewares, so they write to the same file
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="tmp/complex_input_schema_server.log",
        filemode="a",
    )

setup_logging()
logger = logging.getLogger(__name__)

logger.info("complex_input_schema_server starting up")

server = FastMCP("Complex input schema")
server.add_middleware(DereferenceForClaudeMiddleware())

class WordItem(TypedDict):
    word: str
    length: int


@server.tool
def complex_input_schema_tool(
    numbers: Annotated[list[float], Field(description="An array of numbers")],
    strings: Annotated[list[str], Field(description="An array of strings")],
    objects: Annotated[list[dict], Field(description="An array of objects (dicts)")],
    typed_objects: Annotated[list[dict[str, str | int]], Field(description="An array of objects with 'word' (str) and 'length' (int) properties")],
    structured_objects: Annotated[list[WordItem], Field(description="An array of structured objects with defined word and length properties")],
    mixed: Annotated[list[Any], Field(description="An array of non-uniform types (int, str, bool, dict, etc.)")],
    str_and_int: Annotated[list[str | int], Field(description="An array containing only strings and integers")]
) -> str:
    """Tool that handles complex input schemas with mixed-type arrays."""
    return f"Received {len(numbers)} numbers, {len(objects)} objects, {len(mixed)} mixed items, {len(str_and_int)} str/int items, {len(typed_objects)} typed objects, and {len(structured_objects)} structured objects"


def main():
    server.run()


if __name__ == "__main__":
    main()

# Not-dereferenced:
#
#   {
#     "tools": [
#       {
#         "name": "complex_input_schema_tool",
#         "description": "Tool that handles complex input schemas with mixed-type arrays.",
#         "inputSchema": {
#           "type": "object",
#           "properties": {
#             "numbers": {
#               "description": "An array of numbers",
#               "items": {
#                 "type": "number"
#               },
#               "title": "Numbers",
#               "type": "array"
#             },
#             "strings": {
#               "description": "An array of strings",
#               "items": {
#                 "type": "string"
#               },
#               "title": "Strings",
#               "type": "array"
#             },
#             "objects": {
#               "description": "An array of objects (dicts)",
#               "items": {
#                 "additionalProperties": true,
#                 "type": "object"
#               },
#               "title": "Objects",
#               "type": "array"
#             },
#             "typed_objects": {
#               "description": "An array of objects with 'word' (str) and 'length' (int) properties",
#               "items": {
#                 "additionalProperties": {
#                   "anyOf": [
#                     {
#                       "type": "string"
#                     },
#                     {
#                       "type": "integer"
#                     }
#                   ]
#                 },
#                 "type": "object"
#               },
#               "title": "Typed Objects",
#               "type": "array"
#             },
#             "structured_objects": {
#               "description": "An array of structured objects with defined word and length properties",
#               "items": {
#                 "$ref": "#/$defs/WordItem"
#               },
#               "title": "Structured Objects",
#               "type": "array"
#             },
#             "mixed": {
#               "description": "An array of non-uniform types (int, str, bool, dict, etc.)",
#               "items": {},
#               "title": "Mixed",
#               "type": "array"
#             },
#             "str_and_int": {
#               "description": "An array containing only strings and integers",
#               "items": {
#                 "anyOf": [
#                   {
#                     "type": "string"
#                   },
#                   {
#                     "type": "integer"
#                   }
#                 ]
#               },
#               "title": "Str And Int",
#               "type": "array"
#             }
#           },
#           "required": [
#             "numbers",
#             "strings",
#             "objects",
#             "typed_objects",
#             "structured_objects",
#             "mixed",
#             "str_and_int"
#           ],
#           "$defs": {
#             "WordItem": {
#               "properties": {
#                 "word": {
#                   "title": "Word",
#                   "type": "string"
#                 },
#                 "length": {
#                   "title": "Length",
#                   "type": "integer"
#                 }
#               },
#               "required": [
#                 "word",
#                 "length"
#               ],
#               "title": "WordItem",
#               "type": "object"
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
