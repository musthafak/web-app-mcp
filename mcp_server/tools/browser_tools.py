"""Browser-related tools for the MCP Server."""
import logging
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
from playwright.sync_api import (  # type: ignore [import-not-found]
    Error as PlaywrightError,
    Playwright,
    sync_playwright
)

# Configure basic logging
# Using __name__ for the logger name is a common practice.
logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements, too-many-branches
def launch_browser(
        mcp_server, browser_name: str = 'chromium', headless: bool = True
):
    """
    Launches the specified browser and creates a new browser context.

    Args:
        mcp_server: The MCPServer instance.
        browser_name: Name of the browser ('chromium', 'firefox', 'webkit').
        headless: Whether to run the browser in headless mode.

    Returns:
        A message indicating success or failure.
    """
    if mcp_server.browser:
        logger.warning("Browser launch requested but browser is already running.")
        return (
            "Browser is already running. Close the existing browser "
            "before launching a new one."
        )

    if not hasattr(mcp_server, 'playwright') or not mcp_server.playwright:
        try:
            # sync_playwright().start() is correct for Playwright initialization
            mcp_server.playwright = sync_playwright().start()
            logger.info("Playwright started successfully.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to start Playwright: %s", e, exc_info=True)
            return f"Error starting Playwright: {e}"  # End of E501 candidate

    try:
        # Type of mcp_server.playwright is Optional[Playwright],
        # but at this point, it should be Playwright.
        # Adding an assertion or check can be useful for type checkers if needed.
        if mcp_server.playwright is None:
            # This should ideally not happen if the above block succeeded.
            logger.error("Playwright not initialized before browser launch.")
            return "Error: Playwright not initialized."

        browser_instance: Playwright = mcp_server.playwright

        if browser_name == 'chromium':
            mcp_server.browser = browser_instance.chromium.launch(headless=headless)
        elif browser_name == 'firefox':
            mcp_server.browser = browser_instance.firefox.launch(headless=headless)
        elif browser_name == 'webkit':
            mcp_server.browser = browser_instance.webkit.launch(headless=headless)
        else:
            logger.warning("Unsupported browser requested: %s", browser_name)
            return (
                f"Unsupported browser: {browser_name}. Choose from chromium, "
                "firefox, or webkit."
            )

        mcp_server.context = mcp_server.browser.new_context()
        mode = 'in headless mode' if headless else 'with UI'
        logger.info("%s browser launched successfully %s.", browser_name, mode)
        return f"{browser_name} browser launched successfully."
    except PlaywrightError as e:
        logger.error(
            "PWE launching browser %s: %s", browser_name, e, exc_info=True
        )
        # Attempt to clean up playwright if browser launch fails
        if hasattr(mcp_server, 'playwright') and mcp_server.playwright:
            try:
                mcp_server.playwright.stop()
            except Exception as stop_e:  # pylint: disable=broad-except
                logger.error("Playwright cleanup error: %s", stop_e)
            mcp_server.playwright = None
        return f"Playwright Error launching browser {browser_name}: {e}"
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Error launching browser %s: %s", browser_name, e, exc_info=True
        )
        if hasattr(mcp_server, 'playwright') and mcp_server.playwright:
            try:
                mcp_server.playwright.stop()
            except Exception as stop_e:  # pylint: disable=broad-except
                logger.error("Playwright cleanup error: %s", stop_e)
            mcp_server.playwright = None
        return f"Error launching browser {browser_name}: {e}"


def close_browser(mcp_server):  # R0912
    """
    Closes the browser, context, page, and stops Playwright.

    Args:
        mcp_server: The MCPServer instance.

    Returns:
        A message indicating what was closed or if nothing was active.
    """
    closed_something = False
    # Close page first
    if hasattr(mcp_server, 'page') and mcp_server.page:
        try:
            if not mcp_server.page.is_closed():
                mcp_server.page.close()
                logger.info("Page closed.")
        except PlaywrightError as e:
            logger.warning("Failed to close page (PWE): %s", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Failed to close page (EXC): %s", e)
        mcp_server.page = None  # type: ignore
        closed_something = True

    # Close context
    if hasattr(mcp_server, 'context') and mcp_server.context:
        try:
            mcp_server.context.close()
            logger.info("Browser context closed.")
        except PlaywrightError as e:
            logger.warning("Failed to close context (PWE): %s", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Failed to close context (EXC): %s", e)
        mcp_server.context = None  # type: ignore
        closed_something = True

    # Close browser
    if hasattr(mcp_server, 'browser') and mcp_server.browser:
        try:
            mcp_server.browser.close()
            logger.info("Browser closed.")
        except PlaywrightError as e:
            logger.warning("Failed to close browser (PWE): %s", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Failed to close browser (EXC): %s", e)
        mcp_server.browser = None  # type: ignore
        closed_something = True

    # Stop Playwright
    if hasattr(mcp_server, 'playwright') and mcp_server.playwright:
        try:
            mcp_server.playwright.stop()
            logger.info("Playwright stopped.")
        except PlaywrightError as e:
            logger.warning("Failed to stop Playwright (PWE): %s", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Failed to stop Playwright (EXC): %s", e)
        mcp_server.playwright = None
        closed_something = True

    if closed_something:
        return "Browser and related resources closed successfully."
    return "No active browser or Playwright instance to close."


# pylint: disable=too-many-branches
def new_page(mcp_server):
    """
    Creates a new page in the current browser context.
    Closes any existing page before creating a new one.

    Args:
        mcp_server: The MCPServer instance.

    Returns:
        A message indicating success or failure.
    """
    if not hasattr(mcp_server, 'context') or mcp_server.context is None:
        logger.error("New page requested but browser context not available.")
        return (
            "Error: Browser context not available. Launch a browser first."
        )

    # Close existing page if it's open
    if (hasattr(mcp_server, 'page') and
            mcp_server.page and
            not mcp_server.page.is_closed()):
        try:
            mcp_server.page.close()
            logger.info("Closed existing page before creating a new one.")
        except PlaywrightError as e:
            logger.warning("Failed to close existing page (PWE): %s", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Failed to close existing page (EXC): %s", e)
        mcp_server.page = None  # Ensure page attribute is reset

    try:
        # Ensure context is not None before using it
        if mcp_server.context is None:  # Should be caught by the first check
            logger.error("Context became None unexpectedly before new_page.")
            return "Error: Browser context lost before creating new page."
        mcp_server.page = mcp_server.context.new_page()
        logger.info("New page created successfully.")
        return "New page created successfully."
    except PlaywrightError as e:
        logger.error("Playwright error creating new page: %s", e, exc_info=True)
        return f"Playwright error creating new page: {e}"
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Generic error creating new page: %s", e, exc_info=True)
        return f"Error creating new page: {e}"
