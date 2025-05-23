import logging
from playwright.sync_api import Page, Error, TimeoutError as PlaywrightTimeoutError

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def click_element(mcp_server, selector: str):
    """
    Clicks the element specified by selector on mcp_server.page.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."
    
    page: Page = mcp_server.page
    try:
        page.click(selector)
        logging.info(f"Element {selector} clicked successfully.")
        return f"Element {selector} clicked successfully."
    except PlaywrightTimeoutError:
        logging.error(f"Timeout error clicking element {selector}. Element may not be visible or interactable.")
        return f"Timeout error clicking element {selector}. Element may not be visible or interactable."
    except Error as e: # More general Playwright error
        logging.error(f"Playwright error clicking element {selector}: {e}")
        return f"Playwright error clicking element {selector}: {e}"
    except Exception as e:
        logging.error(f"Error clicking element {selector}: {e}")
        return f"Error clicking element {selector}: {e}"

def fill_element(mcp_server, selector: str, text: str):
    """
    Fills the input field specified by selector with text on mcp_server.page.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.fill(selector, text)
        logging.info(f"Text '{text}' filled into element {selector} successfully.")
        return f"Text '{text}' filled into element {selector} successfully."
    except PlaywrightTimeoutError:
        logging.error(f"Timeout error filling element {selector}. Element may not be visible or an input field.")
        return f"Timeout error filling element {selector}. Element may not be visible or an input field."
    except Error as e:
        logging.error(f"Playwright error filling element {selector}: {e}")
        return f"Playwright error filling element {selector}: {e}"
    except Exception as e:
        logging.error(f"Error filling element {selector}: {e}")
        return f"Error filling element {selector}: {e}"

def capture_elements(mcp_server, selector: str):
    """
    Finds all elements matching selector on mcp_server.page and captures their details.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        elements = page.query_selector_all(selector)
        if not elements:
            return f"No elements found matching selector: {selector}"

        results = []
        for element in elements:
            details = {
                'innerText': element.inner_text(),
                'innerHTML': element.inner_html(),
                'attributes': {attr['name']: attr['value'] for attr in element.evaluate_handle('el => Array.from(el.attributes).map(attr => ({name: attr.name, value: attr.value}))').json_value()}
            }
            results.append(details)
        logging.info(f"Captured details for {len(results)} elements matching {selector}.")
        return results
    except Error as e:
        logging.error(f"Playwright error capturing elements with selector {selector}: {e}")
        return f"Playwright error capturing elements with selector {selector}: {e}"
    except Exception as e:
        logging.error(f"Error capturing elements with selector {selector}: {e}")
        return f"Error capturing elements with selector {selector}: {e}"

def evaluate_element(mcp_server, selector: str, expression: str):
    """
    Finds the first element matching selector and evaluates the JavaScript expression in its context.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        element = page.query_selector(selector)
        if not element:
            return f"Error: Element not found for selector: {selector}"
        
        result = element.evaluate(expression)
        logging.info(f"Evaluated expression '{expression}' on element {selector}. Result: {result}")
        return result
    except Error as e: # Playwright error
        logging.error(f"Playwright error evaluating expression '{expression}' on element {selector}: {e}")
        return f"Playwright error evaluating expression '{expression}' on element {selector}: {e}"
    except Exception as e:
        logging.error(f"Error evaluating expression '{expression}' on element {selector}: {e}")
        return f"Error evaluating expression '{expression}' on element {selector}: {e}"

def get_element_attribute(mcp_server, selector: str, attribute_name: str):
    """
    Gets the value of attribute_name for the first element matching selector.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        element = page.query_selector(selector)
        if not element:
            return f"Error: Element not found for selector: {selector}"
        
        attribute_value = element.get_attribute(attribute_name)
        if attribute_value is None:
            logging.info(f"Attribute '{attribute_name}' not found for element {selector}.")
            return f"Attribute '{attribute_name}' not found for element {selector}."
        
        logging.info(f"Retrieved attribute '{attribute_name}' for element {selector}. Value: {attribute_value}")
        return attribute_value
    except Error as e: # Playwright error
        logging.error(f"Playwright error getting attribute '{attribute_name}' for element {selector}: {e}")
        return f"Playwright error getting attribute '{attribute_name}' for element {selector}: {e}"
    except Exception as e:
        logging.error(f"Error getting attribute '{attribute_name}' for element {selector}: {e}")
        return f"Error getting attribute '{attribute_name}' for element {selector}: {e}"

def get_text_content(mcp_server, selector: str):
    """
    Gets the textContent of the first element matching selector.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        element = page.query_selector(selector)
        if not element:
            return f"Error: Element not found for selector: {selector}"
        
        text_content = element.text_content()
        logging.info(f"Retrieved text content for element {selector}.")
        return text_content
    except Error as e: # Playwright error
        logging.error(f"Playwright error getting text content for element {selector}: {e}")
        return f"Playwright error getting text content for element {selector}: {e}"
    except Exception as e:
        logging.error(f"Error getting text content for element {selector}: {e}")
        return f"Error getting text content for element {selector}: {e}"

def wait_for_selector(mcp_server, selector: str, timeout: int = 30000):
    """
    Waits for an element matching selector to appear on mcp_server.page within the given timeout.
    """
    if not hasattr(mcp_server, 'page') or mcp_server.page is None:
        return "Error: Page not initialized. Call 'new_page' first."

    page: Page = mcp_server.page
    try:
        page.wait_for_selector(selector, timeout=float(timeout))
        logging.info(f"Element {selector} found.")
        return f"Element {selector} found."
    except PlaywrightTimeoutError:
        logging.warning(f"Timeout ({timeout}ms) waiting for element {selector}.")
        return f"Timeout waiting for element {selector}."
    except Error as e: # More general Playwright error
        logging.error(f"Playwright error waiting for selector {selector}: {e}")
        return f"Playwright error waiting for selector {selector}: {e}"
    except Exception as e:
        logging.error(f"Error waiting for selector {selector}: {e}")
        return f"Error waiting for selector {selector}: {e}"
