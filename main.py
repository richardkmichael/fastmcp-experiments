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


# server = FastMCP("Empty", version="1.2.3")

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


import asyncio
import logging
from typing import Set
from fastmcp import Context

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='tmp/progress-notifications.log',
    filemode='a'
)

background_tasks: Set[asyncio.Task] = set()

server = FastMCP("Progress", version="1.2.3")

async def background_work(count: int, ctx: Context) -> None:
    for message_number in range(1, count + 1):
        message = f'Background {message_number}'
        logging.info(message)
        await ctx.report_progress(progress=message_number, message=message)
        await asyncio.sleep(2)

@server.tool
async def send_progress(ctx: Context, count: int = 20) -> str:
    task = asyncio.create_task(background_work(count, ctx))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    await asyncio.sleep(10)

    return "Done"



def main():
    server.run()

if __name__ == "__main__":
    main()
