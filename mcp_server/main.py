import logging
from fastmcp import FastMCP
from playwright.sync_api import sync_playwright
from mcp_server.tools import browser_tools, page_tools, element_tools

# Configure basic logging
logging.basicConfig(level=logging.INFO)

class MCPServer(FastMCP):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playwright = None # Will be initialized by launch_browser if needed
        self.browser = None
        self.context = None
        self.page = None
        logging.info("MCP Server initialized")
        self._register_tools()

    def _register_tools(self):
        self.register_tool("launch_browser", browser_tools.launch_browser)
        self.register_tool("close_browser", browser_tools.close_browser)
        self.register_tool("new_page", browser_tools.new_page)
        self.register_tool("goto_page", page_tools.goto_page)
        self.register_tool("capture_screenshot", page_tools.capture_screenshot)
        self.register_tool("close_page", page_tools.close_page)
        self.register_tool("click_element", element_tools.click_element)
        self.register_tool("fill_element", element_tools.fill_element)
        self.register_tool("capture_elements", element_tools.capture_elements)
        self.register_tool("evaluate_element", element_tools.evaluate_element)
        self.register_tool("get_element_attribute", element_tools.get_element_attribute)
        self.register_tool("get_text_content", element_tools.get_text_content)
        self.register_tool("wait_for_selector", element_tools.wait_for_selector)
        logging.info("Browser, Page, and Element tools registered.")

    def shutdown(self):
        logging.info("MCP Server shutting down...")
        browser_tools.close_browser(self) # Ensure browser and Playwright are closed
        logging.info("MCP Server shutdown complete.")


if __name__ == "__main__":
    host = "localhost"
    port = 8765
    server = MCPServer()
    
    logging.info(f"MCP Server attempting to start on {host}:{port}")
    
    try:
        # This is where you would typically start the FastMCP server.
        # server.run(host=host, port=port)
        # For the purpose of this task, we'll simulate it being ready.
        logging.info(f"MCP Server is notionally running on {host}:{port}")
        logging.info("To test, you would interact with the server through its API (e.g., making tool calls).")
        # Keep the main thread alive, or implement server.run() as per FastMCP's documentation.
        # For now, we'll just log and then perform a clean shutdown.
        # In a real application, the server would run indefinitely until a stop signal.
        
        # Example of using a tool if the server was actually running and receiving commands:
        # print(server.tool_handler.execute_tool("launch_browser", {"browser_name": "chromium", "headless": True}))
        # print(server.tool_handler.execute_tool("new_page", {}))
        # print(server.tool_handler.execute_tool("close_browser", {}))

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received.")
    except Exception as e:
        logging.error(f"An error occurred during server operation: {e}")
    finally:
        server.shutdown()
