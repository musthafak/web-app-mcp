"""
Main module for the Multi-Context Playwright (MCP) Server.

This module initializes and runs the MCP server, which provides browser automation
capabilities through WebSocket connections. It leverages FastMCP for communication
handling and Playwright for browser automation.
"""

import asyncio
import logging
from typing import Any

from fastmcp import FastMCP

from mcp_server.tool_manager import ToolManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_LOGGER = logging.getLogger(__name__)


class MCPServer(FastMCP):
    """
    Multi-Context Playwright Server.

    Provides a server interface for browser automation using Playwright.
    Manages browser instances, contexts, and pages through a collection
    of registered tools that can be called remotely.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the MCPServer instance.

        Sets up the tool manager and registers all available browser automation tools.
        """
        super().__init__(*args, **kwargs)
        self.tool_manager = ToolManager()
        _LOGGER.info("MCP Server initialized")
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all available browser automation tools with FastMCP."""
        # Browser management tools
        self.add_tool(self.tool_manager.launch_browser, "launch_browser")
        self.add_tool(self.tool_manager.shutdown, "close_browser")

        # Page management tools
        self.add_tool(self.tool_manager.new_page, "new_page")
        self.add_tool(self.tool_manager.goto_page, "goto_page")
        self.add_tool(self.tool_manager.close_page, "close_page")
        self.add_tool(self.tool_manager.wait_for_navigation, "wait_for_navigation")

        # Page information tools
        self.add_tool(self.tool_manager.get_current_url, "get_current_url")
        self.add_tool(self.tool_manager.get_page_title, "get_page_title")
        self.add_tool(self.tool_manager.capture_screenshot, "capture_screenshot")

        # Element interaction tools
        self.add_tool(self.tool_manager.click_element, "click_element")
        self.add_tool(self.tool_manager.hover_element, "hover_element")
        self.add_tool(self.tool_manager.fill_element, "fill_element")
        self.add_tool(self.tool_manager.select_option, "select_option")
        self.add_tool(self.tool_manager.wait_for_selector, "wait_for_selector")

        # Element information tools
        self.add_tool(self.tool_manager.capture_elements, "capture_elements")
        self.add_tool(self.tool_manager.evaluate_element, "evaluate_element")
        self.add_tool(self.tool_manager.get_element_attribute, "get_element_attribute")
        self.add_tool(self.tool_manager.get_text_content, "get_text_content")
        self.add_tool(self.tool_manager.get_element_html, "get_element_html")
        self.add_tool(
            self.tool_manager.get_element_bounding_box, "get_element_bounding_box"
        )
        self.add_tool(self.tool_manager.capture_area_snapshot, "capture_area_snapshot")

        _LOGGER.info("All browser automation tools registered")

    async def shutdown(self) -> None:
        """Gracefully shut down the server and release all Playwright resources."""
        _LOGGER.info("MCP Server shutting down...")
        await self.tool_manager.shutdown()
        _LOGGER.info("MCP Server shutdown complete")


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8765

    server = MCPServer()
    _LOGGER.info("Starting MCP Server on %s:%s", HOST, PORT)

    try:
        # Start the FastMCP server using Server-Sent Events transport
        server.run(transport="sse")
    except KeyboardInterrupt:
        _LOGGER.info("Keyboard interrupt received. Shutting down...")
    except Exception as e:  # pylint: disable=broad-exception-caught
        _LOGGER.error("Unexpected server error: %s", e, exc_info=True)
    finally:
        asyncio.run(server.shutdown())
