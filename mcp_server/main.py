"""
Main module for the Multi-Context Playwright (MCP) Server.

This module initializes and runs the MCP server, which uses FastMCP
to handle WebSocket connections and browser automation tools.
"""
import logging
from typing import Optional

from fastmcp import FastMCP
# sync_playwright is needed for type hinting if Playwright objects are
# directly instantiated. Here, it's mainly for Playwright, Browser types.
# pylint: disable=import-error
from playwright.sync_api import (  # type: ignore [import-not-found] # noqa: E501
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from mcp_server.tools import browser_tools, element_tools, page_tools

# Configure basic logging
# TODO: Consider moving logging configuration to a separate function or module
# for more complex setups (e.g., different levels for different modules).
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        logger.info("MCP Server initialized")
        self._register_tools()

    def _register_tools(self):
        """Registers all available browser automation tools."""
        # Reversing argument order for add_tool: func first, then name.
        self.add_tool(browser_tools.launch_browser, "launch_browser")
        self.add_tool(browser_tools.close_browser, "close_browser")
        self.add_tool(browser_tools.new_page, "new_page")
        self.add_tool(page_tools.goto_page, "goto_page")
        self.add_tool(page_tools.capture_screenshot, "capture_screenshot")
        self.add_tool(page_tools.close_page, "close_page")
        self.add_tool(element_tools.click_element, "click_element")
        self.add_tool(element_tools.fill_element, "fill_element")
        self.add_tool(element_tools.capture_elements, "capture_elements")
        self.add_tool(element_tools.evaluate_element, "evaluate_element")
        self.add_tool(element_tools.get_element_attribute, "get_element_attribute")
        self.add_tool(element_tools.get_text_content, "get_text_content")
        self.add_tool(element_tools.wait_for_selector, "wait_for_selector")
        logger.info("Browser, Page, and Element tools registered.")

    def shutdown(self):
        """Gracefully shuts down the server and Playwright resources."""
        logger.info("MCP Server shutting down...")
        # Ensure browser and Playwright are closed.
        # The close_browser tool is designed to handle the server instance.
        browser_tools.close_browser(self)
        logger.info("MCP Server shutdown complete.")


if __name__ == "__main__":
    HOST = "localhost"  # pylint: disable=invalid-name
    PORT = 8765         # pylint: disable=invalid-name
    # TODO: Consider making HOST/PORT configurable via env vars/CLI args.

    server = MCPServer()

    logger.info("MCP Server init %s:%s", HOST, PORT)  # Shortened more

    try:
        # This is where you would typically start the FastMCP server.
        server.run(host=HOST, port=PORT)
        # The following lines are for simulation if server.run() is non-blocking
        # or for testing purposes. In a typical FastMCP setup, .run() is
        # blocking.
        # logger.info("MCP Server notionally running on %s:%s", HOST, PORT)
        # logger.info(
        #     "To test, interact with the server via its API (tool calls)."
        # )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    except Exception as e:  # pylint: disable=broad-except
        # Broad exception for unexpected server errors.
        # Specific errors should be handled by FastMCP or tools.
        logger.error("Unexpected server error: %s", e, exc_info=True)
    finally:
        server.shutdown()
