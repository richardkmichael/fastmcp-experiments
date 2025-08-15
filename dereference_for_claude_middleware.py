#!/usr/bin/env python3
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
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class DereferenceForClaudeMiddleware(Middleware):
    """
    Middleware that automatically dereferences JSON schemas for Claude clients
    to fix compatibility issues with $ref references.
    """

    def __init__(self):
        logger.info("Server configured with DereferenceForClaudeMiddleware")

    def _is_claude_client(self, client_name: str) -> bool:
        """Check if the client is a Claude client that needs schema dereferencing."""
        return client_name in [
            "claude-desktop",
            "claude-code",
            "mcp-inspector",
        ]

    # === Schema Dereferencing Implementation: extracted from deref-schema PR

    @staticmethod
    def _detect_self_reference(schema: dict) -> bool:
        """
        Detect if the schema contains self-referencing definitions.

        Args:
            schema: The JSON schema to check

        Returns:
            True if self-referencing is detected
        """
        defs = schema.get("$defs", {})

        def find_refs_in_value(value: Any, parent_def: str) -> bool:
            """Check if a value contains a reference to its parent definition."""
            if isinstance(value, dict):
                if "$ref" in value:
                    ref_path = value["$ref"]
                    # Check if this references the parent definition
                    if ref_path == f"#/$defs/{parent_def}":
                        return True
                # Check all values in the dict
                for v in value.values():
                    if find_refs_in_value(v, parent_def):
                        return True
            elif isinstance(value, list):
                # Check all items in the list
                for item in value:
                    if find_refs_in_value(item, parent_def):
                        return True
            return False

        # Check each definition for self-reference
        for def_name, def_content in defs.items():
            if find_refs_in_value(def_content, def_name):
                # Self-reference detected, return original schema
                return True

        return False

    @staticmethod
    def dereference_json_schema(
        schema: dict, max_depth: int = 5, strip_defs: bool = True
    ) -> dict:
        """
        Dereference a JSON schema by resolving $ref references.

        This function flattens schema properties by:
        1. Check for self-reference - if found, return original schema
        2. When encountering $refs in properties, resolve them on-demand
        3. Track visited definitions globally to prevent circular expansion
        4. Optionally remove $defs if strip_defs=True (default)

        Args:
            schema: The JSON schema to flatten
            max_depth: Maximum depth for resolving references (default: 5)
            strip_defs: Remove $defs section after dereferencing (default: True)

        Returns:
            Schema with references resolved and optionally $defs removed
        """
        # Step 1: Check for self-reference
        if DereferenceForClaudeMiddleware._detect_self_reference(schema):
            # Self-referencing detected, return original schema
            return schema

        # Make a deep copy to work with
        result = deepcopy(schema)

        # Keep original $defs for the final result
        defs = deepcopy(schema.get("$defs", {}))

        # Step 2: Define resolution function that tracks visits globally
        def resolve_refs_in_value(value: Any, depth: int, visiting: set[str]) -> Any:
            """
            Recursively resolve $refs in a value.

            Args:
                value: The value to process
                depth: Current depth in resolution
                visiting: Set of definitions currently being resolved (for cycle detection)

            Returns:
                Value with $refs resolved (or kept if max depth reached)
            """
            if depth >= max_depth:
                return value

            if isinstance(value, dict):
                if "$ref" in value:
                    ref_path = value["$ref"]

                    # Only handle internal references to $defs
                    if ref_path.startswith("#/$defs/"):
                        def_name = ref_path.split("/")[-1]

                        # Check for circular reference
                        if def_name in visiting:
                            # Circular reference detected, keep the $ref
                            return value

                        if def_name in defs:
                            # Add to visiting set
                            visiting.add(def_name)

                            # Get the definition and resolve any refs within it
                            resolved = resolve_refs_in_value(
                                deepcopy(defs[def_name]), depth + 1, visiting
                            )

                            # Remove from visiting set
                            visiting.remove(def_name)

                            # Merge resolved definition with additional properties
                            # Additional properties from the original object take precedence
                            for key, val in value.items():
                                if key != "$ref":
                                    resolved[key] = val

                            return resolved
                        else:
                            # Definition not found, keep the $ref
                            return value
                    else:
                        # External ref or other type - keep as is
                        return value
                else:
                    # Regular dict - process all values
                    return {
                        key: resolve_refs_in_value(val, depth, visiting)
                        for key, val in value.items()
                    }
            elif isinstance(value, list):
                # Process each item in the list
                return [resolve_refs_in_value(item, depth, visiting) for item in value]
            else:
                # Primitive value - return as is
                return value

        # Step 3: Process main schema properties with shared visiting set
        for key, value in result.items():
            if key != "$defs":
                # Each top-level property gets its own visiting set
                # This allows the same definition to be used in different contexts
                result[key] = resolve_refs_in_value(value, 0, set())

        # Step 4: Optionally preserve or remove $defs
        if strip_defs:
            # Remove $defs since all references have been dereferenced
            result.pop("$defs", None)
        else:
            # Preserve original $defs
            if "$defs" in schema:
                result["$defs"] = defs

        return result

    # === Middleware Hooks ===

    async def on_initialize(self, context: MiddlewareContext, call_next):
        """Detect Claude clients and store on session object."""
        client_info = getattr(context.message, "clientInfo", None)
        client_name = (
            getattr(client_info, "name", "unknown") if client_info else "unknown"
        )

        is_claude_client = self._is_claude_client(client_name)

        # HACK: Store client type directly on session object
        if hasattr(context, "session") and context.session:
            context.session.is_claude_client = is_claude_client

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

        # HACK: Read client type from session object (stored during initialization)
        is_claude_client = False
        if context.fastmcp_context and context.fastmcp_context.session:
            is_claude_client = getattr(
                context.fastmcp_context.session, "is_claude_client", False
            )

        if is_claude_client:
            for tool in tools:
                original_schema = deepcopy(tool.parameters)
                dereferenced_schema = self.dereference_json_schema(tool.parameters)

                if original_schema != dereferenced_schema:
                    tool.parameters = dereferenced_schema

        return tools
