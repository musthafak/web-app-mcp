import logging
from playwright.sync_api import Playwright, Browser, BrowserContext, Page, Error

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def launch_browser(mcp_server, browser_name: str = 'chromium', headless: bool = True):
    """
    Launches the specified browser and creates a new browser context.
    """
    if mcp_server.browser:
        return "Browser is already running. Close the existing browser before launching a new one."

    if not hasattr(mcp_server, 'playwright') or mcp_server.playwright is None:
        try:
            from playwright.sync_api import sync_playwright
            mcp_server.playwright = sync_playwright().start()
            logging.info("Playwright started successfully.")
        except Exception as e:
            logging.error(f"Failed to start Playwright: {e}")
            return f"Error starting Playwright: {e}"

    try:
        browser_instance: Playwright = mcp_server.playwright
        if browser_name == 'chromium':
            mcp_server.browser: Browser = browser_instance.chromium.launch(headless=headless)
        elif browser_name == 'firefox':
            mcp_server.browser: Browser = browser_instance.firefox.launch(headless=headless)
        elif browser_name == 'webkit':
            mcp_server.browser: Browser = browser_instance.webkit.launch(headless=headless)
        else:
            return f"Unsupported browser: {browser_name}. Choose from 'chromium', 'firefox', or 'webkit'."
        
        mcp_server.context: BrowserContext = mcp_server.browser.new_context()
        logging.info(f"{browser_name} browser launched successfully {'in headless mode' if headless else ''}.")
        return f"{browser_name} browser launched successfully."
    except Error as e: # Playwright-specific error
        logging.error(f"Playwright Error launching browser {browser_name}: {e}")
        # Attempt to clean up playwright if browser launch fails
        if hasattr(mcp_server, 'playwright') and mcp_server.playwright:
            mcp_server.playwright.stop()
            mcp_server.playwright = None
        return f"Playwright Error launching browser {browser_name}: {e}"
    except Exception as e:
        logging.error(f"Error launching browser {browser_name}: {e}")
        # Attempt to clean up playwright if browser launch fails
        if hasattr(mcp_server, 'playwright') and mcp_server.playwright:
            mcp_server.playwright.stop()
            mcp_server.playwright = None
        return f"Error launching browser {browser_name}: {e}"

def close_browser(mcp_server):
    """
    Closes the browser and Playwright instance.
    """
    closed_something = False
    if hasattr(mcp_server, 'page') and mcp_server.page:
        try:
            mcp_server.page.close()
            logging.info("Page closed.")
        except Exception as e:
            logging.warning(f"Could not close page: {e}")
        mcp_server.page = None
        closed_something = True

    if hasattr(mcp_server, 'context') and mcp_server.context:
        try:
            mcp_server.context.close()
            logging.info("Browser context closed.")
        except Exception as e:
            logging.warning(f"Could not close browser context: {e}")
        mcp_server.context = None
        closed_something = True

    if hasattr(mcp_server, 'browser') and mcp_server.browser:
        try:
            mcp_server.browser.close()
            logging.info("Browser closed.")
        except Exception as e:
            logging.warning(f"Could not close browser: {e}")
        mcp_server.browser = None
        closed_something = True

    if hasattr(mcp_server, 'playwright') and mcp_server.playwright:
        try:
            mcp_server.playwright.stop()
            logging.info("Playwright stopped.")
        except Exception as e:
            logging.warning(f"Could not stop Playwright: {e}")
        mcp_server.playwright = None
        closed_something = True
    
    if closed_something:
        return "Browser and related resources closed successfully."
    else:
        return "No active browser or Playwright instance to close."

def new_page(mcp_server):
    """
    Creates a new page in the current browser context.
    """
    if not hasattr(mcp_server, 'context') or mcp_server.context is None:
        return "Error: Browser context not available. Launch a browser first."
    
    if hasattr(mcp_server, 'page') and mcp_server.page and not mcp_server.page.is_closed():
        try:
            mcp_server.page.close() # Close existing page before creating a new one
            logging.info("Closed existing page before creating a new one.")
        except Exception as e:
            logging.warning(f"Could not close existing page: {e}")


    try:
        mcp_server.page: Page = mcp_server.context.new_page()
        logging.info("New page created successfully.")
        return "New page created successfully."
    except Exception as e:
        logging.error(f"Error creating new page: {e}")
        return f"Error creating new page: {e}"
