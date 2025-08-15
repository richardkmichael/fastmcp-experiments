from fastmcp import FastMCP

server = FastMCP("Exceptions")

@server.tool()
def no_argument_tool() -> None:
    return "Look ma, no argument required!"


def main():
    server.run()

if __name__ == "__main__":
    main()
