from fastmcp import FastMCP

#
# Empty server

#   Generates empty components objects; but not, for example `completions: {}`.
#
#   Spec language is the same.
#
server = FastMCP("Empty", version="1.2.3")


def main():
    server.run()


if __name__ == "__main__":
    main()


# {
#   "capabilities": {
#     "experimental": {},
#     "prompts": {
#       "listChanged": false
#     },
#     "resources": {
#       "subscribe": false,
#       "listChanged": false
#     },
#     "tools": {
#       "listChanged": true
#     }
#   },
#   "serverInfo": {
#     "name": "Empty",
#     "version": "1.2.3"
#   }
# }
