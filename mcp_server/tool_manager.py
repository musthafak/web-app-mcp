"""Manages browser automation tools using Playwright."""

import base64
import logging

# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
from bs4 import BeautifulSoup, Comment
from playwright.async_api import (
    Error as PlaywrightError,
)  # type: ignore [import-not-found]
from playwright.async_api import Page, Playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

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
    async def launch_browser(
        self, browser_name: str = "chromium", headless: bool = False
    ):
        """
        Launches the specified browser and creates a new browser context.

        Args:
            browser_name: Name of the browser ('chromium', 'firefox', 'webkit').
            headless: Whether to run the browser in headless mode.

        Returns:
            A message indicating success or failure.
        """
        headless = False
        if self.browser:
            logger.warning(
                "Browser launch requested but browser is " "already running."
            )
            return (
                "Browser is already running. Close the existing browser "
                "before launching a new one."
            )

        if not hasattr(self, "playwright") or not self.playwright:
            try:
                # async_playwright().start() is correct for Playwright init
                self.playwright = await async_playwright().start()
                logger.info("Playwright started successfully.")
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Failed to start Playwright: %s", e, exc_info=True)
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

            if browser_name == "chromium":
                self.browser = await browser_instance.chromium.launch(headless=headless)
            elif browser_name == "firefox":
                self.browser = await browser_instance.firefox.launch(headless=headless)
            elif browser_name == "webkit":
                self.browser = await browser_instance.webkit.launch(headless=headless)
            else:
                logger.warning("Unsupported browser requested: %s", browser_name)
                return (
                    f"Unsupported browser: {browser_name}. Choose from "
                    "chromium, firefox, or webkit."
                )

            self.context = await self.browser.new_context()
            mode = "in headless mode" if headless else "with UI"
            logger.info("%s browser launched successfully %s.", browser_name, mode)
            return f"{browser_name} browser launched successfully."
        except PlaywrightError as e:
            logger.error("PWE launching browser %s: %s", browser_name, e, exc_info=True)
            # Attempt to clean up playwright if browser launch fails
            if hasattr(self, "playwright") and self.playwright:
                try:
                    await self.playwright.stop()
                except Exception as stop_e:  # pylint: disable=broad-except
                    logger.error("Playwright cleanup error: %s", stop_e)
                self.playwright = None
            return f"Playwright Error launching browser {browser_name}: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error launching browser %s: %s", browser_name, e, exc_info=True
            )
            if hasattr(self, "playwright") and self.playwright:
                try:
                    await self.playwright.stop()
                except Exception as stop_e:  # pylint: disable=broad-except
                    logger.error("Playwright cleanup error: %s", stop_e)
                self.playwright = None
            return f"Error launching browser {browser_name}: {e}"

    async def shutdown(self):  # R0912
        """
        Closes the browser, context, page, and stops Playwright.

        Returns:
            A message indicating what was closed or if nothing was active.
        """
        closed_something = False
        # Close page first
        if hasattr(self, "page") and self.page:
            try:
                if not self.page.is_closed():
                    await self.page.close()
                    logger.info("Page closed.")
            except PlaywrightError as e:
                logger.warning("Failed to close page (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to close page (EXC): %s", e)
            self.page = None  # type: ignore
            closed_something = True

        # Close context
        if hasattr(self, "context") and self.context:
            try:
                await self.context.close()
                logger.info("Browser context closed.")
            except PlaywrightError as e:
                logger.warning("Failed to close context (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to close context (EXC): %s", e)
            self.context = None  # type: ignore
            closed_something = True

        # Close browser
        if hasattr(self, "browser") and self.browser:
            try:
                await self.browser.close()
                logger.info("Browser closed.")
            except PlaywrightError as e:
                logger.warning("Failed to close browser (PWE): %s", e)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to close browser (EXC): %s", e)
            self.browser = None  # type: ignore
            closed_something = True

        # Stop Playwright
        if hasattr(self, "playwright") and self.playwright:
            try:
                await self.playwright.stop()
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
    async def new_page(self):
        """
        Creates a new page in the current browser context.
        Closes any existing page before creating a new one.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, "context") or self.context is None:
            logger.error("New page requested but browser context not " "available.")
            return "Error: Browser context not available. Launch a browser first."

        # Close existing page if it's open
        if hasattr(self, "page") and self.page and not self.page.is_closed():
            try:
                await self.page.close()
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
            self.page = await self.context.new_page()
            logger.info("New page created successfully.")
            return "New page created successfully."
        except PlaywrightError as e:
            logger.error("Playwright error creating new page: %s", e, exc_info=True)
            return f"Playwright error creating new page: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Generic error creating new page: %s", e, exc_info=True)
            return f"Error creating new page: {e}"

    async def goto_page(self, url: str):
        """
        Navigates the current page to the specified URL.

        Args:
            url: The URL to navigate to.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("goto_page called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            await page.goto(url, timeout=90000)
            logger.info("Successfully navigated to %s", url)
            return f"Navigation to {url} successful."
        except PlaywrightError as e:
            logger.error("Playwright nav error for %s: %s", url, e, exc_info=True)
            return f"Playwright nav error to {url}: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error navigating to %s: %s", url, e, exc_info=True)
            return f"Error navigating to {url}: {e}"

    async def capture_area_snapshot(self, selector: str = None):
        """
        Captures the W3C Accessibility Object Model (AOM) representation of the
        current page or a specific element's subtree.

        If a `selector` is provided, the snapshot is taken for the element
        identified by that selector. This corresponds to Playwright's
        `page.accessibility.snapshot(root=element_handle)` where `root`
        specifies the root element for the snapshot. If the element is not found,
        an error is returned.

        If `selector` is `None` or an empty string, the snapshot is taken for the
        entire page.

        Args:
            selector: Optional CSS selector for the root element of the accessibility
                      tree snapshot. If None, captures the whole page.

        Returns:
            A dictionary representing the AOM, or an error message string.
            The dictionary can be large and complex.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error(
                "capture_area_snapshot called but page not initialized or closed."
            )
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        page: Page = self.page
        snapshot = None
        try:
            if selector:
                element_handle = await page.query_selector(selector)
                if not element_handle:
                    logger.warning(
                        "Element not found for selector in capture_area_snapshot: %s",
                        selector,
                    )
                    return f"Error: Element not found for selector: {selector}"
                # Ensure element is visible for a meaningful snapshot
                await element_handle.scroll_into_view_if_needed()
                snapshot = await page.accessibility.snapshot(root=element_handle)
                logger.info(
                    "Captured AOM snapshot for element with selector: %s", selector
                )
            else:
                snapshot = await page.accessibility.snapshot()
                logger.info("Captured AOM snapshot for the entire page.")
            
            return snapshot
        except PlaywrightError as e:
            log_msg = (
                f"Playwright error capturing AOM snapshot for selector {selector if selector else 'page'}: {e}"
            )
            logger.error(log_msg, exc_info=True)
            return f"Playwright error capturing AOM snapshot: {e}"
        except Exception as e:
            log_msg = (
                f"Generic error capturing AOM snapshot for selector {selector if selector else 'page'}: {e}"
            )
            logger.error(log_msg, exc_info=True)
            return f"Error capturing AOM snapshot: {e}"

    async def capture_screenshot(self):
        """
        Captures a screenshot of the current page and returns it as a base64
        encoded string.

        Returns:
            A base64 encoded string of the screenshot, or an error message.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("capture_screenshot called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            screenshot_bytes = await page.screenshot()
            base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
            logger.info("Screenshot captured and encoded to base64.")
            return base64_image
        except PlaywrightError as e:
            logger.error(
                "Playwright error capturing screenshot: %s",
                e,
                exc_info=True,
            )
            return f"Playwright error capturing screenshot: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error capturing screenshot: %s", e, exc_info=True)
            return f"Error capturing screenshot: {e}"

    async def get_current_url(self):
        """
        Gets the current URL of the active page.

        Returns:
            The current URL as a string, or an error message if no page is active.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error("get_current_url called but page not initialized or closed.")
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        page: Page = self.page
        try:
            current_url = page.url
            logger.info("Retrieved current URL: %s", current_url)
            return current_url
        except PlaywrightError as e:
            logger.error("Playwright error getting current URL: %s", e, exc_info=True)
            return f"Playwright error getting current URL: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error getting current URL: %s", e, exc_info=True)
            return f"Error getting current URL: {e}"

    async def get_page_title(self):
        """
        Gets the title of the current active page.

        Returns:
            The page title as a string, or an error message if no page is active.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error("get_page_title called but page not initialized or closed.")
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        page: Page = self.page
        try:
            title = await page.title()
            logger.info("Retrieved page title: %s", title)
            return title
        except PlaywrightError as e:
            logger.error("Playwright error getting page title: %s", e, exc_info=True)
            return f"Playwright error getting page title: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error getting page title: %s", e, exc_info=True)
            return f"Error getting page title: {e}"

    async def wait_for_navigation(
        self, url: str = None, wait_until: str = None, timeout: float = None
    ):
        """
        Waits for the page to navigate to a new URL or for a page load event to occur.
        This is typically used after an action that causes navigation, like a click.

        Args:
            url: Optional. A glob pattern, regex pattern, or full URL to match the
                 target URL. If not specified, waits for the next navigation to any URL.
            wait_until: Optional. The load state to wait for. Common values include:
                        'load': Wait for the 'load' event.
                        'domcontentloaded': Wait for the 'DOMContentLoaded' event.
                        'networkidle': Wait until there are no network connections for
                                       at least 500 ms.
                        If None, Playwright's default is used (typically 'load').
            timeout: Optional. Maximum time to wait for navigation in seconds.
                     If None, Playwright's default timeout (usually 30 seconds) is used.

        Returns:
            A message indicating success or failure of the navigation wait.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error(
                "wait_for_navigation called but page not initialized or closed."
            )
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        page: Page = self.page
        options = {}
        if url is not None:
            options["url"] = url
        if wait_until is not None:
            # Playwright's type hint for wait_until is Literal["load", "domcontentloaded", "networkidle", "commit"]
            # We'll rely on the user to provide a valid string based on documentation.
            options["wait_until"] = wait_until  # type: ignore
        if timeout is not None:
            options["timeout"] = timeout * 1000  # Convert seconds to milliseconds

        try:
            response = await page.wait_for_navigation(**options)
            if response:
                logger.info(
                    "Successfully waited for navigation. Final URL: %s. Status: %s",
                    response.url,
                    response.status,
                )
                return f"Navigation completed. Final URL: {response.url}"
            else: # Should not happen if wait_for_navigation resolves without error
                logger.info("Successfully waited for navigation (no response object).")
                return "Navigation completed (no response object)."

        except PlaywrightTimeoutError as e:
            timeout_sec = (
                options.get("timeout", 30000) / 1000
            )  # Use provided or default 30s
            err_msg = (
                f"Timeout ({timeout_sec}s) waiting for navigation "
                f"(URL: {url}, wait_until: {wait_until}). {e}"
            )
            logger.warning(err_msg)
            return err_msg
        except PlaywrightError as e:
            logger.error(
                "Playwright error waiting for navigation "
                "(URL: %s, wait_until: %s): %s",
                url,
                wait_until,
                e,
                exc_info=True,
            )
            return f"Playwright error waiting for navigation: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Generic error waiting for navigation "
                "(URL: %s, wait_until: %s): %s",
                url,
                wait_until,
                e,
                exc_info=True,
            )
            return f"Error waiting for navigation: {e}"

    async def close_page(self):
        """
        Closes the current page.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.info("close_page called but no active page to close.")
            return "No active page to close."

        page: Page = self.page
        try:
            if not page.is_closed():
                await page.close()
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

    async def click_element(self, selector: str):
        """
        Clicks the element specified by selector on the current page.

        Args:
            selector: The CSS selector for the element to click.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("click_element called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            await page.click(selector, timeout=3000)
            logger.info("Element %s clicked successfully.", selector)
            return f"Element {selector} clicked successfully."
        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout clicking element %s. " "May not be visible/interactable.",
                selector,
            )
            return (
                f"Timeout clicking {selector}. Element may not be visible "
                "or interactable."  # Shortened
            )
        except PlaywrightError as e:
            logger.error("PWE clicking %s: %s", selector, e, exc_info=True)
            return f"PWE clicking {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error clicking %s: %s", selector, e, exc_info=True)
            return f"Error clicking {selector}: {e}"  # Shortened

    async def hover_element(self, selector: str):
        """
        Hovers over the element specified by the selector on the current page.

        Args:
            selector: The CSS selector for the element to hover over.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error("hover_element called but page not initialized or closed.")
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        page: Page = self.page
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning(
                    "Element not found for selector in hover_element: %s", selector
                )
                return f"Error: Element not found for selector: {selector}"

            await element.hover(timeout=3000)  # Default timeout for hover is often short
            logger.info("Successfully hovered over element %s.", selector)
            return f"Successfully hovered over element {selector}."
        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout hovering over element %s. Element might not be "
                "visible or interactable for hover.",
                selector,
            )
            return (
                f"Timeout hovering over {selector}. Element may not be "
                "visible or interactable for hover."
            )
        except PlaywrightError as e:
            logger.error(
                "Playwright error hovering over element %s: %s",
                selector,
                e,
                exc_info=True,
            )
            return f"Playwright error hovering over {selector}: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error hovering over element %s: %s", selector, e, exc_info=True
            )
            return f"Error hovering over element {selector}: {e}"

    async def fill_element(self, selector: str, text: str):
        """
        Fills the input field specified by selector with text on the current
        page.

        Args:
            selector: The CSS selector for the input field.
            text: The text to fill into the input field.

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("fill_element called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            await page.fill(selector, text, timeout=3000)
            logger.info(
                "Text '%s' filled into element %s successfully.", text, selector
            )
            return f"Text '{text}' filled into element {selector} successfully."
        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout filling element %s. " "May not be visible or an input field.",
                selector,
            )
            return (
                f"Timeout filling {selector}. Element may not be visible "
                "or an input field."  # Shortened
            )
        except PlaywrightError as e:
            logger.error("PWE filling %s: %s", selector, e, exc_info=True)
            return f"PWE filling {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error filling %s: %s", selector, e, exc_info=True)
            return f"Error filling {selector}: {e}"  # Shortened

    async def select_option(
        self,
        selector: str,
        option_value: str = None,
        option_label: str = None,
        option_index: int = None,
    ):
        """
        Selects an option within a <select> element identified by the selector.
        Exactly one of `option_value`, `option_label`, or `option_index` must be provided.

        Args:
            selector: The CSS selector for the <select> element.
            option_value: The value attribute of the option to select.
            option_label: The visible text (label) of the option to select.
            option_index: The 0-based index of the option to select.

        Returns:
            A message indicating success and the value(s) of the selected option(s),
            or an error message.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error("select_option called but page not initialized or closed.")
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        provided_options = sum(
            o is not None for o in [option_value, option_label, option_index]
        )
        if provided_options == 0:
            return "Error: No option specifier provided. Use option_value, option_label, or option_index."
        if provided_options > 1:
            return "Error: Multiple option specifiers provided. Only one of option_value, option_label, or option_index should be used."

        page: Page = self.page
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning(
                    "Select element not found for selector: %s", selector
                )
                return f"Error: Select element not found for selector: {selector}"

            select_arg = {}
            selection_method_used = ""
            if option_value is not None:
                select_arg = {"value": option_value}
                selection_method_used = f"value '{option_value}'"
            elif option_label is not None:
                select_arg = {"label": option_label}
                selection_method_used = f"label '{option_label}'"
            elif option_index is not None:
                select_arg = {"index": option_index}
                selection_method_used = f"index {option_index}"
            
            # Type hint for select_arg to match Playwright's expectations
            # (Union[str, ElementHandle, Dict, List[str], List[ElementHandle], List[Dict], None])
            # In our case, it's Dict[str, Union[str, int]]
            selected_values = await element.select_option(select_arg, timeout=5000) # type: ignore

            if not selected_values:
                # This can happen if the option wasn't found by Playwright, though it often throws an error.
                # Or if the select_option call itself didn't result in any change.
                logger.warning(
                    "No option was selected for element %s using %s. "
                    "The option might not exist or match the criteria.",
                    selector,
                    selection_method_used,
                )
                return (
                    f"Error: Could not select option using {selection_method_used} "
                    f"for element {selector}. Option may not exist or match."
                )

            logger.info(
                "Successfully selected option(s) with value(s): %s for element %s using %s.",
                selected_values,
                selector,
                selection_method_used,
            )
            return (
                f"Successfully selected option(s) with value(s): {selected_values} "
                f"for element {selector} using {selection_method_used}."
            )
        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout selecting option for element %s using %s.",
                selector,
                selection_method_used,
            )
            return (
                f"Timeout selecting option for {selector} using {selection_method_used}. "
                "Option may not be visible or interactable."
            )
        except PlaywrightError as e:
            # Playwright might throw a generic Error if the option is not found
            # e.g., "Error: Element.selectOption: Element is not a <select> element"
            # or "Error: Element.selectOption: No option found for specified value(s)"
            logger.error(
                "Playwright error selecting option for element %s using %s: %s",
                selector,
                selection_method_used,
                e,
                exc_info=True,
            )
            return (
                f"Playwright error selecting option for {selector} using {selection_method_used}: {e}"
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Generic error selecting option for element %s using %s: %s",
                selector,
                selection_method_used,
                e,
                exc_info=True,
            )
            return f"Error selecting option for element {selector} using {selection_method_used}: {e}"

    async def capture_elements(self, selector: str):
        """
        Finds all elements matching selector and captures their details.

        Details include innerText, innerHTML, and attributes.

        Args:
            selector: The CSS selector for the elements.

        Returns:
            A list of dictionaries containing element details, or an error
            message.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("capture_elements called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            elements = await page.query_selector_all(selector)
            if not elements:
                logger.info("No elements found matching selector: %s", selector)
                return f"No elements found matching selector: {selector}"

            results = []
            for element in elements:
                # Note: evaluate_handle and json_value can be slow if overused.
                attributes_script = (
                    "el => Array.from(el.attributes)"
                    ".map(attr => ({name: attr.name, value: attr.value}))"
                )
                attributes_handle = await element.evaluate_handle(attributes_script)
                attributes = await attributes_handle.json_value()
                attributes = {attr["name"]: attr["value"] for attr in attributes}
                details = {
                    "innerText": await element.inner_text(),
                    "innerHTML": await element.inner_html(),
                    "attributes": attributes,
                }
                results.append(details)
            logger.info(
                "Captured details for %d elements matching %s.", len(results), selector
            )
            return results
        except PlaywrightError as e:
            logger.error(
                "Playwright error capturing elements with selector %s: %s",
                selector,
                e,
                exc_info=True,
            )
            return f"PWE capturing elements for {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error capturing elements for %s: %s", selector, e, exc_info=True
            )
            return f"Error capturing elements for {selector}: {e}"  # Shortened

    async def evaluate_element(self, selector: str, expression: str):
        """
        Finds the first element matching selector and evaluates a JavaScript
        expression in its context.

        Args:
            selector: The CSS selector for the element.
            expression: The JavaScript expression to evaluate.

        Returns:
            The result of the evaluation, or an error message.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("evaluate_element called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning("Element not found for selector: %s", selector)
                return f"Error: Element not found for selector: {selector}"

            result = await element.evaluate(expression)
            logger.info(
                "Evaluated expression '%s' on element %s. Result: %s",
                expression,
                selector,
                result,
            )
            return result
        except PlaywrightError as e:
            logger.error(
                "Playwright error evaluating expr '%s' on %s: %s",
                expression,
                selector,
                e,
                exc_info=True,
            )
            return f"PWE evaluating expr '{expression}' on {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error evaluating expr '%s' on %s: %s",
                expression,
                selector,
                e,
                exc_info=True,
            )
            return (  # Shortened
                f"Error evaluating expr '{expression}' on {selector}: {e}"
            )

    async def get_element_html(
        self,
        selector: str,
        char_limit: int = None,
        remove_scripts: bool = False,
        remove_comments: bool = False,
        remove_styles: bool = False,
    ):
        """
        Gets the outerHTML of the first element matching selector, with optional cleanup and truncation.

        Args:
            selector: The CSS selector for the element.
            char_limit: Optional character limit to truncate the HTML.
            remove_scripts: If True, removes <script> tags from the HTML.
            remove_comments: If True, removes HTML comments.
            remove_styles: If True, removes <style> and <link rel="stylesheet"> tags.

        Returns:
            The processed outerHTML of the element, or an error message.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error("get_element_html called but page not initialized or closed.")
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        page: Page = self.page
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning(
                    "Element not found for selector in get_element_html: %s", selector
                )
                return f"Error: Element not found for selector: {selector}"

            outer_html = await element.evaluate("el => el.outerHTML")

            if remove_scripts or remove_comments or remove_styles:
                soup = BeautifulSoup(outer_html, "html.parser")

                if remove_scripts:
                    for script_tag in soup.find_all("script"):
                        script_tag.decompose()

                if remove_comments:
                    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                        comment.extract()
                
                if remove_styles:
                    for style_tag in soup.find_all("style"):
                        style_tag.decompose()
                    for link_tag in soup.find_all("link", rel="stylesheet"):
                        link_tag.decompose()
                
                outer_html = str(soup)

            if char_limit is not None and len(outer_html) > char_limit:
                outer_html = outer_html[:char_limit] + "..."
                logger.info(
                    "HTML for selector %s truncated to %s characters.",
                    selector,
                    char_limit,
                )

            logger.info(
                "Retrieved HTML for element %s (options applied).", selector
            )
            return outer_html
        except PlaywrightError as e:
            logger.error(
                "Playwright error getting HTML for element %s: %s",
                selector,
                e,
                exc_info=True,
            )
            return f"Playwright error getting HTML for {selector}: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error getting HTML for element %s: %s", selector, e, exc_info=True
            )
            return f"Error getting HTML for element {selector}: {e}"

    async def get_element_bounding_box(self, selector: str):
        """
        Gets the bounding box (x, y, width, height) of the first element matching selector.

        Args:
            selector: The CSS selector for the element.

        Returns:
            A dictionary with 'x', 'y', 'width', and 'height' of the element,
            or an error message if the element is not found or not visible.
        """
        if not hasattr(self, "page") or self.page is None or self.page.is_closed():
            logger.error(
                "get_element_bounding_box called but page not initialized or closed."
            )
            return "Error: Page not initialized or has been closed. Call 'new_page' first."

        page: Page = self.page
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning(
                    "Element not found for selector in get_element_bounding_box: %s",
                    selector,
                )
                return f"Error: Element not found for selector: {selector}"

            bounding_box = await element.bounding_box()

            if bounding_box is None:
                logger.warning(
                    "Element %s found, but it has no bounding box (e.g., display:none).",
                    selector,
                )
                return (
                    f"Error: Element {selector} found, but it is not visible or "
                    "has no dimensions."
                )
            
            logger.info(
                "Retrieved bounding box for element %s: %s", selector, bounding_box
            )
            return bounding_box
        except PlaywrightError as e:
            logger.error(
                "Playwright error getting bounding box for element %s: %s",
                selector,
                e,
                exc_info=True,
            )
            return f"Playwright error getting bounding box for {selector}: {e}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error getting bounding box for element %s: %s",
                selector,
                e,
                exc_info=True,
            )
            return f"Error getting bounding box for element {selector}: {e}"

    async def get_element_attribute(self, selector: str, attribute_name: str):
        """
        Gets the value of an attribute for the first element matching selector.

        Args:
            selector: The CSS selector for the element.
            attribute_name: The name of the attribute to get.

        Returns:
            The attribute value, or an error/info message if not found.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("get_element_attribute called but page not " "initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning("Element not found for selector: %s", selector)
                return f"Error: Element not found for selector: {selector}"

            attribute_value = await element.get_attribute(attribute_name)
            if attribute_value is None:
                logger.info(
                    "Attribute '%s' not found for element %s.", attribute_name, selector
                )
                return (
                    f"Attribute '{attribute_name}' not found for "
                    f"element {selector}."
                )

            logger.info(
                "Retrieved attribute '%s' for %s. Value: %s",
                attribute_name,
                selector,
                attribute_value,
            )
            return attribute_value
        except PlaywrightError as e:
            logger.error(
                "Playwright error getting attr '%s' for %s: %s",
                attribute_name,
                selector,
                e,
                exc_info=True,
            )
            return (  # Shortened
                f"PWE getting attr '{attribute_name}' for {selector}: {e}"
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error getting attr '%s' for %s: %s",
                attribute_name,
                selector,
                e,
                exc_info=True,
            )
            return (  # Shortened
                f"Error getting attr '{attribute_name}' for {selector}: {e}"
            )

    async def get_text_content(self, selector: str):
        """
        Gets the textContent of the first element matching selector.

        Args:
            selector: The CSS selector for the element.

        Returns:
            The text content, or an error message.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("get_text_content called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning("Element not found for selector: %s", selector)
                return f"Error: Element not found for selector: {selector}"

            text_content = await element.text_content()
            logger.info("Retrieved text content for element %s.", selector)
            return text_content
        except PlaywrightError as e:
            logger.error(
                "Playwright error getting text content for element %s: %s",
                selector,
                e,
                exc_info=True,
            )
            return f"PWE getting text for {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error getting text for %s: %s", selector, e, exc_info=True)
            return f"Error getting text for {selector}: {e}"  # Shortened

    async def wait_for_selector(self, selector: str, timeout: int = 30000):
        """
        Waits for an element matching selector to appear on the page
        within the given timeout.

        Args:
            selector: The CSS selector to wait for.
            timeout: Maximum time to wait in milliseconds (default 30s).

        Returns:
            A message indicating success or failure.
        """
        if not hasattr(self, "page") or self.page is None:
            logger.error("wait_for_selector called but page not initialized.")
            return "Error: Page not initialized. Call 'new_page' first."

        page: Page = self.page
        try:
            await page.wait_for_selector(selector, timeout=float(timeout))
            logger.info("Element %s found.", selector)
            return f"Element {selector} found."
        except PlaywrightTimeoutError:
            logger.warning("Timeout (%sms) waiting for element %s.", timeout, selector)
            return f"Timeout waiting for element {selector}."
        except PlaywrightError as e:
            logger.error("PWE waiting for %s: %s", selector, e, exc_info=True)
            return f"PWE waiting for {selector}: {e}"  # Shortened
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error waiting for %s: %s", selector, e, exc_info=True)
            return f"Error waiting for {selector}: {e}"  # Shortened