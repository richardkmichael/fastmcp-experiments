# Tolerate imports throughout the file, not requiring them at the top; useful for experimental code
# ruff: noqa: E402
"""
DereferenceForClaudeMiddleware

Middleware that automatically dereferences JSON schemas for Claude clients
to fix compatibility issues with $ref references.

Claude Desktop and Claude Code fail to properly handle schemas with $ref
references, sending null values instead of valid parameters. This middleware
detects these clients during initialization and automatically dereferences
schemas in tool, prompt, and resource responses.
"""

import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.middleware.schema_dereference import dereference_json_schema


class DereferenceForClaudeMiddleware(Middleware):
    def __init__(self):
        logger.info("Server configured with DereferenceForClaudeMiddleware")

    def _get_client_name(self, context: MiddlewareContext) -> str:
        """Extract client name from initialize request context."""
        params = getattr(context.message, "params", None)
        client_info = getattr(params, "clientInfo", None) if params else None
        return getattr(client_info, "name", "unknown") if client_info else "unknown"

    def _is_claude_client(self, client_name: str) -> bool:
        """Check if the client is a Claude client that needs schema dereferencing."""
        return client_name in [
            "claude-desktop",
            "claude-code",
            "inspector-client",
        ]

    # === Middleware Hooks ===

    async def on_initialize(self, context: MiddlewareContext, call_next):
        """Detect Claude clients and store client type in context state."""
        client_name = self._get_client_name(context)
        is_claude_client = self._is_claude_client(client_name)

        # Store client type in context state for use in subsequent hooks
        if context.fastmcp_context:
            context.fastmcp_context.set_state("client_name", client_name)
            context.fastmcp_context.set_state("is_claude_client", is_claude_client)

        if is_claude_client:
            logger.info(
                f"on_initialize: 🤖 {client_name} detected - schemas will be dereferenced"
            )
        else:
            logger.info(
                f"on_initialize: {client_name} detected - schemas will be unchanged"
            )

        return await call_next(context)

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """Dereference tool schemas for Claude clients."""
        tools = await call_next(context)

        # Read client type from context state (set during initialization)
        if context.fastmcp_context and context.fastmcp_context.get_state(
            "is_claude_client"
        ):
            for tool in tools:
                original_schema = deepcopy(tool.parameters)
                dereferenced_schema = dereference_json_schema(tool.parameters)

                if original_schema != dereferenced_schema:
                    tool.parameters = dereferenced_schema

        return tools


# === Subclass implementation ===

from fastmcp.server.middleware.schema_dereference import SchemaDereferenceMiddleware


class DereferenceForClaudeMiddlewareSubclass(SchemaDereferenceMiddleware):
    def __init__(self):
        logger.info("Server configured with DereferenceForClaudeMiddlewareSubclass")

    def _get_client_name(self, context: MiddlewareContext) -> str:
        """Extract client name from initialize request context."""
        params = getattr(context.message, "params", None)
        client_info = getattr(params, "clientInfo", None) if params else None
        return getattr(client_info, "name", "unknown") if client_info else "unknown"

    def _is_claude_client(self, client_name: str) -> bool:
        """Check if the client is a Claude client that needs schema dereferencing."""
        return client_name in [
            "claude-desktop",
            "claude-code",
            "inspector-client",
        ]

    # === Middleware Hooks ===

    async def on_initialize(self, context: MiddlewareContext, call_next):
        """Detect Claude clients and store client type in context state."""
        client_name = self._get_client_name(context)
        is_claude_client = self._is_claude_client(client_name)

        # Store client type in context state for use in subsequent hooks
        if context.fastmcp_context:
            context.fastmcp_context.set_state("client_name", client_name)
            context.fastmcp_context.set_state("is_claude_client", is_claude_client)

        if is_claude_client:
            logger.info(
                f"on_initialize: 🤖 {client_name} detected - schemas will be dereferenced"
            )
        else:
            logger.info(
                f"on_initialize: {client_name} detected - schemas will be unchanged"
            )

        return await call_next(context)

    # If Claude, use parent class dereferencing
    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """Dereference tool schemas for Claude clients."""

        # Read client type from context state (set during initialization)
        if context.fastmcp_context and context.fastmcp_context.get_state(
            "is_claude_client"
        ):
            return await super().on_list_tools(context, call_next)
        else:
            return await call_next(context)


from dataclasses import asdict
from pprint import pformat

from jsonref import JsonRefError, replace_refs


class DereferenceForClaudeMiddlewareSimple(Middleware):
    def __init__(self):
        logger.info("Server configured with DereferenceForClaudeMiddlewareSimple")

    def _get_client_name(self, context: MiddlewareContext) -> str:
        """Extract client name from initialize request context."""
        params = getattr(context.message, "params", None)
        client_info = getattr(params, "clientInfo", None) if params else None
        return getattr(client_info, "name", "unknown") if client_info else "unknown"

    def _is_claude_client(self, client_name: str) -> bool:
        """Check if the client is a Claude client that needs schema dereferencing."""
        return client_name in [
            "claude-desktop",
            "claude-code",
            "inspector-client",
        ]

    def _dereference_tool(self, tool, remove_defs=True):
        """Dereference a tool's schema, returning the modified tool or None on failure.

        Args:
            tool: Tool object with parameters schema to dereference
            remove_defs: If True, remove $defs from schema after dereferencing (default: True)
        """
        try:
            # proxies=False returns plain dicts to ensure compatibility with FastMCP
            # lazy_load=False resolves immediately
            dereferenced = replace_refs(tool.parameters, proxies=False, lazy_load=False)

            # If requested, remove $defs (since all references have been resolved)
            if remove_defs and isinstance(dereferenced, dict) and "$defs" in dereferenced:
                dereferenced = {k: v for k, v in dereferenced.items() if k != "$defs"}

            tool.parameters = dereferenced
            return tool

        except JsonRefError as e:
            logger.warning(
                f"Failed to dereference schema for tool '{tool.name}': {e}. "
                "Tool will be hidden from client."
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error dereferencing schema for tool '{tool.name}': {e}. "
                "Tool will be hidden from client."
            )
            return None

    # === Middleware Hooks ===

    async def on_initialize(self, context: MiddlewareContext, call_next):
        """Detect Claude clients and store client type on the session."""

        # Dump context for debugging, but handle fastmcp_context specially
        ctx_dict = asdict(context)

        # Replace fastmcp_context with a simple representation to avoid property access
        if context.fastmcp_context:
            ctx_dict['fastmcp_context'] = f"<Context object at {hex(id(context.fastmcp_context))}>"

        logger.info(f"on_initialize: Context:\n{pformat(ctx_dict, width=120)}")

        client_name = self._get_client_name(context)
        is_claude_client = self._is_claude_client(client_name)

        # Store on the SESSION (persists across requests), not context (single request only)
        # FIXME: Accessing .session causes:
        # 2025-10-17 12:24:54,443 - root - WARNING - Failed to validate request: Context is not available outside of a request
        if context.fastmcp_context:
            session = context.fastmcp_context.session
            logger.info(
                f"session: {session}"
            )
            setattr(session, "_is_claude_client", is_claude_client)
            setattr(session, "_client_name", client_name)

        if is_claude_client:
            logger.info(
                f"on_initialize: 🤖 {client_name} detected - will dereference schemas"
            )
        else:
            logger.info(
                f"on_initialize: {client_name} detected - schemas will be unchanged"
            )

        return await call_next(context)

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """Dereference tool schemas for Claude clients using jsonref."""

        # Dump context for debugging, but handle fastmcp_context specially
        ctx_dict = asdict(context)

        # Replace fastmcp_context with a simple representation to avoid property access
        if context.fastmcp_context:
            ctx_dict['fastmcp_context'] = f"<Context object at {hex(id(context.fastmcp_context))}>"

        logger.info(f"on_list_tools: Context:\n{pformat(ctx_dict, width=120)}")

        tools = await call_next(context)

        # Read from SESSION (persists across requests)
        if context.fastmcp_context:
            session = context.fastmcp_context.session
            is_claude_client = getattr(session, "_is_claude_client", False)
            client_name = getattr(session, "_client_name", "unknown")

            if True: # is_claude_client:
                logger.info(
                    f"on_list_tools: 🤖 {client_name} - dereferencing schemas"
                )
                tools = [
                    dereferenced_tool
                    for tool in tools
                    if (dereferenced_tool := self._dereference_tool(tool)) is not None
                ]
            else:
                logger.info(
                    f"on_list_tools: {client_name} - schemas unchanged"
                )

        return tools
