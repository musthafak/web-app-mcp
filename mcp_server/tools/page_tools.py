"""Page manipulation tools for the MCP Server."""
import logging
# pylint: disable=import-error
from playwright.sync_api import (  # type: ignore [import-not-found]
    Page, Error as PlaywrightError
)

# Configure basic logging
logger = logging.getLogger(__name__)


def goto_page(mcp_server, url: str):
    """
    Navigates the current page to the specified URL.

    Args:
        mcp_server: The MCPServer instance.
        url: The URL to navigate to.

    Returns:
        A message indicating success or failure.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("goto_page called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.goto(url)
        logger.info("Successfully navigated to %s", url)
        return f"Navigation to {url} successful."
    except PlaywrightError as e:
        logger.error(
            "Playwright nav error for %s: %s", url, e, exc_info=True
        )
        return f"Playwright nav error to {url}: {e}"
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error navigating to %s: %s", url, e, exc_info=True)
        return f"Error navigating to {url}: {e}"


def capture_screenshot(mcp_server, path: str):
    """
    Captures a screenshot of the current page and saves it to the specified path.

    Args:
        mcp_server: The MCPServer instance.
        path: The file path to save the screenshot to.

    Returns:
        A message indicating success or failure.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("capture_screenshot called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.screenshot(path=path)
        logger.info("Screenshot saved to %s", path)
        return f"Screenshot saved to {path}."
    except PlaywrightError as e:
        logger.error(
            "Playwright error capturing screenshot to %s: %s",
            path, e, exc_info=True
        )
        return f"Playwright error capturing screenshot to {path}: {e}"
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Error capturing screenshot to %s: %s", path, e, exc_info=True
        )
        # Consider if the path is valid, writable, etc.
        msg_part1 = f"Error capturing screenshot to {path}: {e}. "
        msg_part2 = "Ensure path is valid/writable."
        return msg_part1 + msg_part2


def close_page(mcp_server):
    """
    Closes the current page.

    Args:
        mcp_server: The MCPServer instance.

    Returns:
        A message indicating success or failure.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.info("close_page called but no active page to close.")
        return "No active page to close."

    page: Page = mcp_server.page
    try:
        if not page.is_closed():
            page.close()
            logger.info("Page closed successfully.")
        else:
            logger.info("Page was already closed.")
        mcp_server.page = None  # Reset the page attribute on the server
        return "Page closed successfully."
    except PlaywrightError as e:
        logger.error("Playwright error closing page: %s", e, exc_info=True)
        mcp_server.page = None  # Attempt to reset even if close fails
        return f"Playwright error closing page: {e}"
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error closing page: %s", e, exc_info=True)
        mcp_server.page = None  # Attempt to reset even if close fails
        return f"Error closing page: {e}"
