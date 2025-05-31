from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError, ToolError

server = FastMCP("Exceptions")

@server.resource("boom://boom")
def boom_resource() -> None:
    raise ResourceError

@server.tool()
def boom_tool() -> None:
    raise ToolError

def main():
    server.run()

if __name__ == "__main__":
    main()
