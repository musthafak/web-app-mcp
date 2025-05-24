import logging
"""Manages browser automation tools using Playwright."""
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
from playwright.sync_api import (  # type: ignore [import-not-found]
    Error as PlaywrightError,
    Page,
    Playwright,
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

# Configure basic logging
# Using __name__ for the logger name is a common practice.
logger = logging.getLogger(__name__)


class ToolManager:
    """
    Manages Playwright browser instances, contexts, and pages for automation.

    This class encapsulates the core Playwright setup and provides methods
    to interact with web pages, including navigation, element interaction,
    and capturing screenshots or data.
    """
    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser = None
        self.context = None
        self.page = None

    # pylint: disable=too-many-return-statements, too-many-branches
    def launch_browser(
        self, browser_name: str = 'chromium', headless: bool = True
    ):
        """
        Launches the specified browser and creates a new browser context.

        Args:
            browser_name: Name of the browser ('chromium', 'firefox', 'webkit').
            headless: Whether to run the browser in headless mode.

        Returns:
            A message indicating success or failure.
        """
        if self.browser:
            logger.warning("Browser launch requested but browser is "
                           "already running.")
            return (
                "Browser is already running. Close the existing browser "
                "before launching a new one."
            )

        if not hasattr(self, 'playwright') or not self.playwright:
            try:
                # sync_playwright().start() is correct for Playwright init
                self.playwright = sync_playwright().start()
                logger.info("Playwright started successfully.")
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Failed to start Playwright: %s", e,
                             exc_info=True)
                # End of E501 candidate
                return f"Error starting Playwright: {e}"

        try:
            # Type of self.playwright is Optional[Playwright],
            # but at this point, it should be Playwright.
            # Adding an assertion or check can be useful for type checkers
            # if needed.
            if self.playwright is None:
                # This should ideally not happen if the above block succeeded.
                logger.error("Playwright not initialized before browser launch.")
                return "Error: Playwright not initialized."

            browser_instance: Playwright = self.playwright

            if browser_name == 'chromium':
                self.browser = browser_instance.chromium.launch(
                    headless=headless)
            elif browser_name == 'firefox':
                self.browser = browser_instance.firefox.launch(
                    headless=headless)
            elif browser_name == 'webkit':
                self.browser = browser_instance.webkit.launch(
                    headless=headless)
            else:
                logger.warning("Unsupported browser requested: %s", browser_name)
                return (
                    f"Unsupported browser: {browser_name}. Choose from "
                    "chromium, firefox, or webkit."
                )

            self.context = self.browser.new_context()
            mode = 'in headless mode' if headless else 'with UI'
            logger.info("%s browser launched successfully %s.", browser_name,
                        mode)
            return f"{browser_name} browser launched successfully."
        except PlaywrightError as e:
            logger.error(
                "PWE launching browser %s: %s", browser_name, e, exc_info=True
            )
            # Attempt to clean up playwright if browser launch fails
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    self.playwright.stop()
                except Exception as stop_e:  # pylint: disable=broad-except
                    logger.error("Playwright cleanup error: %s", stop_e)
                self.playwright = None
            return f"Playwright Error launching browser {browser_name}: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error launching browser %s: %s", browser_name, e,
                exc_info=True
            )
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    self.playwright.stop()
                except Exception as stop_e:  # pylint: disable=broad-except
                    logger.error("Playwright cleanup error: %s", stop_e)
                self.playwright = None
            return f"Error launching browser {browser_name}: {e}"

    def shutdown(self):  # R0912
        """
        Closes the browser, context, page, and stops Playwright.

        Returns:
            A message indicating what was closed or if nothing was active.
        """
        closed_something = False
        # Close page first
        if hasattr(self, 'page') and self.page:
            try:
                if not self.page.is_closed():
                    self.page.close()
                    logger.info("Page closed.")
            except PlaywrightError as e:
                logger.warning("Failed to close page (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to close page (EXC): %s", e)
            self.page = None  # type: ignore
            closed_something = True

        # Close context
        if hasattr(self, 'context') and self.context:
            try:
                self.context.close()
                logger.info("Browser context closed.")
            except PlaywrightError as e:
                logger.warning("Failed to close context (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to close context (EXC): %s", e)
            self.context = None  # type: ignore
            closed_something = True

        # Close browser
        if hasattr(self, 'browser') and self.browser:
            try:
                self.browser.close()
                logger.info("Browser closed.")
            except PlaywrightError as e:
                logger.warning("Failed to close browser (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to close browser (EXC): %s", e)
            self.browser = None  # type: ignore
            closed_something = True

        # Stop Playwright
        if hasattr(self, 'playwright') and self.playwright:
            try:
                self.playwright.stop()
                logger.info("Playwright stopped.")
            except PlaywrightError as e:
                logger.warning("Failed to stop Playwright (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to stop Playwright (EXC): %s", e)
            self.playwright = None
            closed_something = True

        if closed_something:
            return "Browser and related resources closed successfully."
        return "No active browser or Playwright instance to close."

    # pylint: disable=too-many-branches
    def new_page(self):
        """
        Creates a new page in the current browser context.
        Closes any existing page before creating a new one.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, 'context') or self.context is None:
            logger.error("New page requested but browser context not "
                         "available.")
            return (
                "Error: Browser context not available. Launch a browser first."
            )

        # Close existing page if it's open
        if (hasattr(self, 'page') and
                self.page and
                not self.page.is_closed()):
            try:
                self.page.close()
                logger.info("Closed existing page before creating a new one.")
            except PlaywrightError as e:
                logger.warning("Failed to close existing page (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to close existing page (EXC): %s", e)
            self.page = None  # Ensure page attribute is reset

        try:
            # Ensure context is not None before using it
            if self.context is None:  # Should be caught by the first check
                logger.error("Context became None unexpectedly before new_page.")
                return "Error: Browser context lost before creating new page."
            self.page = self.context.new_page()
            logger.info("New page created successfully.")
            return "New page created successfully."
        except PlaywrightError as e:
            logger.error("Playwright error creating new page: %s", e,
                         exc_info=True)
            return f"Playwright error creating new page: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Generic error creating new page: %s", e,
                         exc_info=True)
            return f"Error creating new page: {e}"


    def goto_page(self, url: str):
        """
        Navigates the current page to the specified URL.

        Args:
            url: The URL to navigate to.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("goto_page called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
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

    def capture_screenshot(self, path: str):
        """
        Captures a screenshot of the current page and saves it to the specified
        path.

        Args:
            path: The file path to save the screenshot to.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("capture_screenshot called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
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

    def close_page(self):
        """
        Closes the current page.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.info("close_page called but no active page to close.")
            return "No active page to close."

        page: Page = self.page
        try:
            if not page.is_closed():
                page.close()
                logger.info("Page closed successfully.")
            else:
                logger.info("Page was already closed.")
            self.page = None  # Reset the page attribute on the server
            return "Page closed successfully."
        except PlaywrightError as e:
            logger.error("Playwright error closing page: %s", e, exc_info=True)
            self.page = None  # Attempt to reset even if close fails
            return f"Playwright error closing page: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error closing page: %s", e, exc_info=True)
            self.page = None  # Attempt to reset even if close fails
            return f"Error closing page: {e}"


    def click_element(self, selector: str):
        """
        Clicks the element specified by selector on the current page.

        Args:
            selector: The CSS selector for the element to click.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("click_element called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            page.click(selector)
            logger.info("Element %s clicked successfully.", selector)
            return f"Element {selector} clicked successfully."
        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout clicking element %s. "
                "May not be visible/interactable.",
                selector
            )
            return (
                f"Timeout clicking {selector}. Element may not be visible "
                "or interactable."  # Shortened
            )
        except PlaywrightError as e:
            logger.error(
                "PWE clicking %s: %s", selector, e, exc_info=True
            )
            return f"PWE clicking {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error clicking %s: %s", selector, e, exc_info=True
            )
            return f"Error clicking {selector}: {e}"  # Shortened

    def fill_element(self, selector: str, text: str):
        """
        Fills the input field specified by selector with text on the current
        page.

        Args:
            selector: The CSS selector for the input field.
            text: The text to fill into the input field.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("fill_element called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            page.fill(selector, text)
            logger.info(
                "Text '%s' filled into element %s successfully.", text, selector
            )
            return f"Text '{text}' filled into element {selector} successfully."
        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout filling element %s. "
                "May not be visible or an input field.",
                selector
            )
            return (
                f"Timeout filling {selector}. Element may not be visible "
                "or an input field."  # Shortened
            )
        except PlaywrightError as e:
            logger.error(
                "PWE filling %s: %s", selector, e, exc_info=True
            )
            return f"PWE filling {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error filling %s: %s", selector, e, exc_info=True
            )
            return f"Error filling {selector}: {e}"  # Shortened

    def capture_elements(self, selector: str):
        """
        Finds all elements matching selector and captures their details.

        Details include innerText, innerHTML, and attributes.

        Args:
            selector: The CSS selector for the elements.

        Returns:
            A list of dictionaries containing element details, or an error
            message.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("capture_elements called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            elements = page.query_selector_all(selector)
            if not elements:
                logger.info("No elements found matching selector: %s", selector)
                return f"No elements found matching selector: {selector}"

            results = []
            for element in elements:
                # Note: evaluate_handle and json_value can be slow if overused.
                attributes_script = (
                    'el => Array.from(el.attributes)'
                    '.map(attr => ({name: attr.name, value: attr.value}))'
                )
                attributes_handle = element.evaluate_handle(attributes_script)
                attributes = {
                    attr['name']: attr['value']
                    for attr in attributes_handle.json_value()
                }
                details = {
                    'innerText': element.inner_text(),
                    'innerHTML': element.inner_html(),
                    'attributes': attributes
                }
                results.append(details)
            logger.info(
                "Captured details for %d elements matching %s.",
                len(results), selector
            )
            return results
        except PlaywrightError as e:
            logger.error(
                "Playwright error capturing elements with selector %s: %s",
                selector, e, exc_info=True
            )
            return (
                f"PWE capturing elements for {selector}: {e}"  # Shortened
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error capturing elements for %s: %s",
                selector, e, exc_info=True
            )
            return f"Error capturing elements for {selector}: {e}"  # Shortened

    def evaluate_element(self, selector: str, expression: str):
        """
        Finds the first element matching selector and evaluates a JavaScript
        expression in its context.

        Args:
            selector: The CSS selector for the element.
            expression: The JavaScript expression to evaluate.

        Returns:
            The result of the evaluation, or an error message.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("evaluate_element called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            element = page.query_selector(selector)
            if not element:
                logger.warning("Element not found for selector: %s", selector)
                return f"Error: Element not found for selector: {selector}"

            result = element.evaluate(expression)
            logger.info(
                "Evaluated expression '%s' on element %s. Result: %s",
                expression, selector, result
            )
            return result
        except PlaywrightError as e:
            logger.error(
                "Playwright error evaluating expr '%s' on %s: %s",
                expression, selector, e, exc_info=True
            )
            return (  # Shortened
                f"PWE evaluating expr '{expression}' on {selector}: {e}"
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error evaluating expr '%s' on %s: %s",
                expression, selector, e, exc_info=True
            )
            return (  # Shortened
                f"Error evaluating expr '{expression}' on {selector}: {e}"
            )

    def get_element_attribute(self, selector: str, attribute_name: str):
        """
        Gets the value of an attribute for the first element matching selector.

        Args:
            selector: The CSS selector for the element.
            attribute_name: The name of the attribute to get.

        Returns:
            The attribute value, or an error/info message if not found.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("get_element_attribute called but page not "
                         "initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            element = page.query_selector(selector)
            if not element:
                logger.warning("Element not found for selector: %s", selector)
                return f"Error: Element not found for selector: {selector}"

            attribute_value = element.get_attribute(attribute_name)
            if attribute_value is None:
                logger.info(
                    "Attribute '%s' not found for element %s.",
                    attribute_name, selector
                )
                return (
                    f"Attribute '{attribute_name}' not found for "
                    f"element {selector}."
                )

            logger.info(
                "Retrieved attribute '%s' for %s. Value: %s",
                attribute_name, selector, attribute_value
            )
            return attribute_value
        except PlaywrightError as e:
            logger.error(
                "Playwright error getting attr '%s' for %s: %s",
                attribute_name, selector, e, exc_info=True
            )
            return (  # Shortened
                f"PWE getting attr '{attribute_name}' for {selector}: {e}"
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error getting attr '%s' for %s: %s",
                attribute_name, selector, e, exc_info=True
            )
            return (  # Shortened
                f"Error getting attr '{attribute_name}' for {selector}: {e}"
            )

    def get_text_content(self, selector: str):
        """
        Gets the textContent of the first element matching selector.

        Args:
            selector: The CSS selector for the element.

        Returns:
            The text content, or an error message.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("get_text_content called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            element = page.query_selector(selector)
            if not element:
                logger.warning("Element not found for selector: %s", selector)
                return f"Error: Element not found for selector: {selector}"

            text_content = element.text_content()
            logger.info("Retrieved text content for element %s.", selector)
            return text_content
        except PlaywrightError as e:
            logger.error(
                "Playwright error getting text content for element %s: %s",
                selector, e, exc_info=True
            )
            return (  # Shortened
                f"PWE getting text for {selector}: {e}"
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error getting text for %s: %s", selector, e, exc_info=True
            )
            return f"Error getting text for {selector}: {e}"  # Shortened

    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """
        Waits for an element matching selector to appear on the page
        within the given timeout.

        Args:
            selector: The CSS selector to wait for.
            timeout: Maximum time to wait in milliseconds (default 30s).

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, 'page') or self.page is None:
            logger.error("wait_for_selector called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            page.wait_for_selector(selector, timeout=float(timeout))
            logger.info("Element %s found.", selector)
            return f"Element {selector} found."
        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout (%sms) waiting for element %s.", timeout, selector
            )
            return f"Timeout waiting for element {selector}."
        except PlaywrightError as e:
            logger.error(
                "PWE waiting for %s: %s", selector, e, exc_info=True
            )
            return f"PWE waiting for {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error waiting for %s: %s", selector, e, exc_info=True
            )
            return f"Error waiting for {selector}: {e}"  # Shortened
