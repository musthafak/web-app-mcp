"""
Main module for the Multi-Context Playwright (MCP) Server.

This module initializes and runs the MCP server, which uses FastMCP
to handle WebSocket connections and browser automation tools.
"""

import logging

from fastmcp import FastMCP

from mcp_server.tool_manager import ToolManager

# async_playwright is needed for type hinting if Playwright objects are
# directly instantiated. Here, it's mainly for Playwright, Browser types.
# pylint: disable=import-error
# F401: Unused imports Browser, BrowserContext, Page, Playwright, Optional
# from playwright.async_api import (  # type: ignore [import-not-found] # noqa: E501
#     Browser,
#     BrowserContext,
#     Page,
#     Playwright,
# )
# from typing import Optional


# Configure basic logging
# TODO: Consider moving logging configuration to a separate function or module
# for more complex setups (e.g., different levels for different modules).
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPServer(FastMCP):
    """
    Multi-Context Playwright Server.

    Manages Playwright instances, browsers, contexts, and pages
    to execute browser automation tasks based on tool calls.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the MCPServer instance.

        Sets up Playwright-related attributes and registers tools.
        """
        super().__init__(*args, **kwargs)
        self.tool_manager = ToolManager()
        logger.info("MCP Server initialized")
        self._register_tools()

    def _register_tools(self):
        """Registers all available browser automation tools."""
        # Registering async tools - FastMCP will handle the async/await properly
        self.add_tool(self.tool_manager.launch_browser, "launch_browser")
        # Renamed from close_browser
        self.add_tool(self.tool_manager.shutdown, "close_browser")
        self.add_tool(self.tool_manager.new_page, "new_page")
        self.add_tool(self.tool_manager.goto_page, "goto_page")
        self.add_tool(self.tool_manager.capture_area_snapshot, "capture_area_snapshot")
        self.add_tool(self.tool_manager.close_page, "close_page")
        self.add_tool(self.tool_manager.click_element, "click_element")
        self.add_tool(self.tool_manager.fill_element, "fill_element")
        self.add_tool(self.tool_manager.capture_elements, "capture_elements")
        self.add_tool(self.tool_manager.evaluate_element, "evaluate_element")
        self.add_tool(self.tool_manager.get_element_attribute, "get_element_attribute")
        self.add_tool(self.tool_manager.get_text_content, "get_text_content")
        self.add_tool(self.tool_manager.wait_for_selector, "wait_for_selector")
        logger.info("Browser, Page, and Element tools registered.")

    async def shutdown(self):
        """Gracefully shuts down the server and Playwright resources."""
        logger.info("MCP Server shutting down...")
        await self.tool_manager.shutdown()
        logger.info("MCP Server shutdown complete.")


if __name__ == "__main__":
    HOST = "localhost"  # pylint: disable=invalid-name
    PORT = 8765  # pylint: disable=invalid-name
    # TODO: Consider making HOST/PORT configurable via env vars/CLI args.

    server = MCPServer()

    logger.info("MCP Server init %s:%s", HOST, PORT)  # Shortened more

    try:
        # This is where you would typically start the FastMCP server.
        server.run(transport="sse")
        # The following lines are for simulation if server.run() is non-blocking
        # or for testing purposes. In a typical FastMCP setup, .run() is
        # blocking.
        # logger.info("MCP Server notionally running on %s:%s", HOST, PORT)
        # logger.info("To test, interact with the server via its API "
        # "(tool calls).")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    except Exception as e:  # pylint: disable=broad-except
        # Broad exception for unexpected server errors.
        # Specific errors should be handled by FastMCP or tools.
        logger.error("Unexpected server error: %s", e, exc_info=True)
    finally:
        # Need to use asyncio.run() or similar to call the async shutdown method
        import asyncio

        asyncio.run(server.shutdown())