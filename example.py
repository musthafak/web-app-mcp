import asyncio
import logging
from fastmcp.client import FastMCPClient

# Configure basic logging for the client
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_ADDRESS = "ws://localhost:8765"

async def main():
    logging.info(f"Attempting to connect to MCP server at {SERVER_ADDRESS}")
    try:
        async with FastMCPClient(SERVER_ADDRESS) as client:
            logging.info("Successfully connected to MCP server.")

            # 1. Launch a browser
            logging.info("Requesting to launch browser...")
            launch_result = await client.execute_tool("launch_browser", {"browser_name": "chromium", "headless": True})
            logging.info(f"Launch browser result: {launch_result}")
            if "error" in str(launch_result).lower():
                logging.error("Failed to launch browser. Exiting.")
                return

            # 2. Create a new page
            logging.info("Requesting to create a new page...")
            new_page_result = await client.execute_tool("new_page", {})
            logging.info(f"New page result: {new_page_result}")
            if "error" in str(new_page_result).lower():
                logging.error("Failed to create new page. Attempting to close browser.")
                close_browser_result = await client.execute_tool("close_browser", {})
                logging.info(f"Close browser result: {close_browser_result}")
                return

            # 3. Navigate to a page
            target_url = "https://www.example.com"
            logging.info(f"Requesting to navigate to {target_url}...")
            goto_result = await client.execute_tool("goto_page", {"url": target_url})
            logging.info(f"Goto page result: {goto_result}")
            if "error" in str(goto_result).lower():
                logging.error(f"Failed to navigate to {target_url}.")
            else:
                # 4. Get text content of the main heading
                heading_selector = "h1"
                logging.info(f"Requesting text content of element '{heading_selector}'...")
                text_content_result = await client.execute_tool("get_text_content", {"selector": heading_selector})
                logging.info(f"Get text content result for '{heading_selector}': {text_content_result}")

                # 5. Capture a screenshot
                screenshot_path = "example_screenshot.png"
                logging.info(f"Requesting to capture screenshot to '{screenshot_path}'...")
                screenshot_result = await client.execute_tool("capture_screenshot", {"path": screenshot_path})
                logging.info(f"Capture screenshot result: {screenshot_result}")


            # 6. Close the page
            logging.info("Requesting to close the page...")
            close_page_result = await client.execute_tool("close_page", {})
            logging.info(f"Close page result: {close_page_result}")

            # 7. Close the browser
            logging.info("Requesting to close the browser...")
            close_browser_result = await client.execute_tool("close_browser", {})
            logging.info(f"Close browser result: {close_browser_result}")

    except ConnectionRefusedError:
        logging.error(f"Connection to MCP server at {SERVER_ADDRESS} refused. Ensure the server is running.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Note: FastMCPClient uses asyncio, so we run the main function in an event loop.
    # If you are using Python 3.7+, you can use asyncio.run(main())
    # For broader compatibility (e.g. Python 3.6 which might be in some envs):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info("Client script interrupted by user.")
    finally:
        if loop.is_running():
            loop.close()
        logging.info("Client script finished.")
