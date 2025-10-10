# FastMCP Experiments

The `client_aware_server.py` requires FastMCP from a local path (`../fastmcp`); see `pyproject.toml`.


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
make-mcp-json <SOME_SERVER>.py
```

# Claude Code

## Add with CLI

`claude mcp add [name] uv -- --directory $CWD run <SOME_SERVER>.py`

## Run via `.mcp.json`

Generate an "mcp.json" using the helper (above).

```
# One
claude --strict-mcp-config --mcp-config tmp/some_server.json

# All
claude --strict-mcp-config --mcp-config tmp/all_servers.json
```

# MCP Inspector

`npx @modelcontextprotocol/inspector --config /tmp/some_server.json`
