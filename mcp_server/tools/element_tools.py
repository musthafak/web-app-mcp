"""Element interaction tools for the MCP Server."""
import logging
# pylint: disable=import-error
from playwright.sync_api import (  # type: ignore [import-not-found]
    Page,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError
)

logger = logging.getLogger(__name__)


def click_element(mcp_server, selector: str):
    """
    Clicks the element specified by selector on the current page.

    Args:
        mcp_server: The MCPServer instance.
        selector: The CSS selector for the element to click.

    Returns:
        A message indicating success or failure.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("click_element called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.click(selector)
        logger.info("Element %s clicked successfully.", selector)
        return f"Element {selector} clicked successfully."
    except PlaywrightTimeoutError:
        logger.warning(
            "Timeout clicking element %s. May not be visible/interactable.",
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


def fill_element(mcp_server, selector: str, text: str):
    """
    Fills the input field specified by selector with text on the current page.

    Args:
        mcp_server: The MCPServer instance.
        selector: The CSS selector for the input field.
        text: The text to fill into the input field.

    Returns:
        A message indicating success or failure.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("fill_element called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.fill(selector, text)
        logger.info(
            "Text '%s' filled into element %s successfully.", text, selector
        )
        return f"Text '{text}' filled into element {selector} successfully."
    except PlaywrightTimeoutError:
        logger.warning(
            "Timeout filling element %s. May not be visible or an input field.",
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


def capture_elements(mcp_server, selector: str):
    """
    Finds all elements matching selector and captures their details.

    Details include innerText, innerHTML, and attributes.

    Args:
        mcp_server: The MCPServer instance.
        selector: The CSS selector for the elements.

    Returns:
        A list of dictionaries containing element details, or an error message.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("capture_elements called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
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


def evaluate_element(mcp_server, selector: str, expression: str):
    """
    Finds the first element matching selector and evaluates a JavaScript
    expression in its context.

    Args:
        mcp_server: The MCPServer instance.
        selector: The CSS selector for the element.
        expression: The JavaScript expression to evaluate.

    Returns:
        The result of the evaluation, or an error message.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("evaluate_element called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
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
        return (
            f"PWE evaluating expr '{expression}' on {selector}: {e}"  # Shortened
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Error evaluating expr '%s' on %s: %s",
            expression, selector, e, exc_info=True
        )
        return (
            f"Error evaluating expr '{expression}' on {selector}: {e}" # Shortened
        )


def get_element_attribute(mcp_server, selector: str, attribute_name: str):
    """
    Gets the value of an attribute for the first element matching selector.

    Args:
        mcp_server: The MCPServer instance.
        selector: The CSS selector for the element.
        attribute_name: The name of the attribute to get.

    Returns:
        The attribute value, or an error/info message if not found.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("get_element_attribute called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        element = page.query_selector(selector)
        if not element:
            logger.warning("Element not found for selector: %s", selector)
            return f"Error: Element not found for selector: {selector}"

        attribute_value = element.get_attribute(attribute_name)
        if attribute_value is None:
            logger.info(
                "Attribute '%s' not found for element %s.", attribute_name, selector
            )
            return f"Attribute '{attribute_name}' not found for element {selector}."

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
        return (
            f"PWE getting attr '{attribute_name}' for {selector}: {e}"  # Shortened
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Error getting attr '%s' for %s: %s",
            attribute_name, selector, e, exc_info=True
        )
        return (
            f"Error getting attr '{attribute_name}' for {selector}: {e}" # Shortened
        )


def get_text_content(mcp_server, selector: str):
    """
    Gets the textContent of the first element matching selector.

    Args:
        mcp_server: The MCPServer instance.
        selector: The CSS selector for the element.

    Returns:
        The text content, or an error message.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("get_text_content called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
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
        return (
            f"PWE getting text for {selector}: {e}"  # Shortened
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Error getting text for %s: %s", selector, e, exc_info=True
        )
        return f"Error getting text for {selector}: {e}"  # Shortened


def wait_for_selector(mcp_server, selector: str, timeout: int = 30000):
    """
    Waits for an element matching selector to appear on the page
    within the given timeout.

    Args:
        mcp_server: The MCPServer instance.
        selector: The CSS selector to wait for.
        timeout: Maximum time to wait in milliseconds (default 30s).

    Returns:
        A message indicating success or failure.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        logger.error("wait_for_selector called but page not initialized.")
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
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
