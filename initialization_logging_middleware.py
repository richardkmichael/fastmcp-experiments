#!/usr/bin/env python3
"""
InitializationLoggingMiddleware

A middleware that logs all requests, including initialization,
to demonstrate FastMCP's middleware capabilities.
"""

import logging

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class InitializationLoggingMiddleware(Middleware):
    """Middleware that logs all requests, including initialization."""

    async def on_message(self, context: MiddlewareContext, call_next):
        logger.info(f"📨 on_message: method={context.method}, type={context.type}")
        result = await call_next(context)
        logger.info(f"📨 on_message: method={context.method}")
        return result

    async def on_initialize(self, context: MiddlewareContext, call_next):
        client_info = getattr(context.message, "clientInfo", "Unknown")
        protocol_version = getattr(context.message, "protocolVersion", "Unknown")

        logger.info(f"🚀 on_initialize: {client_info} | Protocol: {protocol_version}")

        # Call the original initialization handler
        result = await call_next(context)

        logger.info("🚀 on_initialize: completed")
        return result
