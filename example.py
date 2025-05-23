"""
Example client script to interact with the MCP Server.

This script demonstrates a sequence of browser automation tasks:
1. Connect to the MCP server.
2. Launch a browser.
3. Create a new page.
4. Navigate to a URL.
5. Extract text content.
6. Capture a screenshot.
7. Close the page and browser.
"""
import asyncio
import logging
from fastmcp import Client

# Configure basic logging for the client
# Using __name__ for the logger name is a common practice.
# However, for a simple script like this, using the root logger is also fine.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SERVER_ADDRESS = "ws://localhost:8765"


async def main():
    """Runs the main client automation sequence."""
    logger.info("Attempting to connect to MCP server at %s", SERVER_ADDRESS)
    try:
        async with Client(SERVER_ADDRESS) as client:
            logger.info("Successfully connected to MCP server.")

            # 1. Launch a browser
            logger.info("Requesting to launch browser...")
            launch_params = {"browser_name": "chromium", "headless": True}
            launch_result = await client.execute_tool("launch_browser", launch_params)
            logger.info("Launch browser result: %s", launch_result)
            if "error" in str(launch_result).lower():
                logger.error("Failed to launch browser. Exiting.")
                return

            # 2. Create a new page
            logger.info("Requesting to create a new page...")
            new_page_result = await client.execute_tool("new_page", {})
            logger.info("New page result: %s", new_page_result)
            if "error" in str(new_page_result).lower():
                logger.error("Failed to create new page. Closing browser.")
                close_browser_result = await client.execute_tool("close_browser", {})
                logger.info("Close browser result: %s", close_browser_result)
                return

            # 3. Navigate to a page
            target_url = "https://www.example.com"
            logger.info("Requesting to navigate to %s...", target_url)
            goto_result = await client.execute_tool("goto_page", {"url": target_url})
            logger.info("Goto page result: %s", goto_result)
            if "error" in str(goto_result).lower():
                logger.error("Failed to navigate to %s.", target_url)
            else:
                # 4. Get text content of the main heading
                heading_selector = "h1"
                logger.info(
                    "Requesting text content of element '%s'...",
                    heading_selector
                )
                text_params = {"selector": heading_selector}
                text_content_result = await client.execute_tool(
                    "get_text_content", text_params
                )
                logger.info(
                    "Get text content result for '%s': %s",
                    heading_selector, text_content_result
                )

                # 5. Capture a screenshot
                screenshot_path = "example_screenshot.png"
                logger.info(
                    "Requesting to capture screenshot to '%s'...",
                    screenshot_path
                )
                screenshot_params = {"path": screenshot_path}
                screenshot_result = await client.execute_tool(
                    "capture_screenshot", screenshot_params
                )
                logger.info("Capture screenshot result: %s", screenshot_result)

            # 6. Close the page
            logger.info("Requesting to close the page...")
            close_page_result = await client.execute_tool("close_page", {})
            logger.info("Close page result: %s", close_page_result)

            # 7. Close the browser
            logger.info("Requesting to close the browser...")
            close_browser_result = await client.execute_tool("close_browser", {})
            logger.info("Close browser result: %s", close_browser_result)

    except ConnectionRefusedError:
        logger.error(
            "Connection to MCP server at %s refused. "
            "Ensure the server is running.", SERVER_ADDRESS
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error("An unexpected error occurred: %s", e, exc_info=True)

if __name__ == "__main__":
    # Note: FastMCPClient (now fastmcp.Client) uses asyncio,
    # so we run the main function in an event loop.
    # Python 3.7+ can use asyncio.run(main()).
    # The following is for broader compatibility (e.g., Python 3.6).
    # pylint: disable=deprecated-method # For asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Client script interrupted by user.")
    finally:
        if loop.is_running():
            # Ensure loop is closed only if it's still running.
            # This can prevent errors if the loop was already closed due to an exception.
            loop.close()
        logger.info("Client script finished.")
