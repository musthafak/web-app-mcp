import logging
from playwright.sync_api import Page, Error

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def goto_page(mcp_server, url: str):
    """
    Navigates the current page to the specified URL.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.goto(url)
        logging.info(f"Successfully navigated to {url}")
        return f"Navigation to {url} successful."
    except Error as e: # Playwright-specific error for navigation
        logging.error(f"Playwright navigation error for {url}: {e}")
        return f"Playwright navigation error to {url}: {e}"
    except Exception as e:
        logging.error(f"Error navigating to {url}: {e}")
        return f"Error navigating to {url}: {e}"

def capture_screenshot(mcp_server, path: str):
    """
    Captures a screenshot of the current page and saves it to the specified path.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.screenshot(path=path)
        logging.info(f"Screenshot saved to {path}")
        return f"Screenshot saved to {path}."
    except Error as e: # Playwright-specific error for screenshot
        logging.error(f"Playwright error capturing screenshot to {path}: {e}")
        return f"Playwright error capturing screenshot to {path}: {e}"
    except Exception as e:
        logging.error(f"Error capturing screenshot to {path}: {e}")
        # Consider if the path is valid, writable, etc.
        return f"Error capturing screenshot to {path}: {e}. Ensure the path is valid and writable."

def close_page(mcp_server):
    """
    Closes the current page.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "No active page to close."

    page: Page = mcp_server.page
    try:
        if not page.is_closed():
            page.close()
            logging.info("Page closed successfully.")
        else:
            logging.info("Page was already closed.")
        mcp_server.page = None
        return "Page closed successfully."
    except Error as e: # Playwright-specific error for closing page
        logging.error(f"Playwright error closing page: {e}")
        mcp_server.page = None # Attempt to reset even if close fails
        return f"Playwright error closing page: {e}"
    except Exception as e:
        logging.error(f"Error closing page: {e}")
        mcp_server.page = None # Attempt to reset even if close fails
        return f"Error closing page: {e}"
