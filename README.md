# FastMCP Experiments

Uses FastMCP from a local path (`../fastmcp`).


MCP JSON helper:

```bash
make-mcp-json() {
  local server_file=$1
  local name=$( basename ${server_file} .py )
  local mcp_json="tmp/${name}.json"

  uv run fastmcp install mcp-json --name ${name} ${server_file} | jq '{ "mcpServers": . }' > ${mcp_json}
}
```


Then:

```
make-mcp-json <SERVER>.py
claude --mcp-config tmp/<SERVER>.json
```
