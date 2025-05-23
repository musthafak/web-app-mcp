import pytest
from unittest.mock import MagicMock, patch
from mcp_server.tools import element_tools
from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

# Mock the MCPServer class structure for attributes, focusing on 'page'
class MockMCPServer:
    def __init__(self):
        self.page = None # This will be a MagicMock instance in tests

@pytest.fixture
def mock_mcp_server():
    """Provides a fresh mock MCPServer instance for each test, with page mocked."""
    server = MockMCPServer()
    server.page = MagicMock()
    return server

@pytest.fixture
def mock_mcp_server_no_page():
    """Provides a mock MCPServer instance where page is initially None."""
    server = MockMCPServer()
    return server

# Common variables
SELECTOR = "button.submit"
TEXT_TO_FILL = "hello world"
EXPRESSION = "element => element.value"
ATTRIBUTE_NAME = "data-testid"
TIMEOUT_MS = 15000

# Tests for click_element
def test_click_element_success(mock_mcp_server):
    result = element_tools.click_element(mock_mcp_server, SELECTOR)
    mock_mcp_server.page.click.assert_called_once_with(SELECTOR)
    assert f"Element {SELECTOR} clicked successfully." in result

def test_click_element_no_page(mock_mcp_server_no_page):
    result = element_tools.click_element(mock_mcp_server_no_page, SELECTOR)
    assert "Error: Page not initialized." in result

def test_click_element_timeout_error(mock_mcp_server):
    mock_mcp_server.page.click.side_effect = PlaywrightTimeoutError("Timeout clicking")
    result = element_tools.click_element(mock_mcp_server, SELECTOR)
    assert f"Timeout error clicking element {SELECTOR}" in result

def test_click_element_playwright_error(mock_mcp_server):
    mock_mcp_server.page.click.side_effect = PlaywrightError("Generic Playwright error")
    result = element_tools.click_element(mock_mcp_server, SELECTOR)
    assert f"Playwright error clicking element {SELECTOR}: Generic Playwright error" in result

# Tests for fill_element
def test_fill_element_success(mock_mcp_server):
    result = element_tools.fill_element(mock_mcp_server, SELECTOR, TEXT_TO_FILL)
    mock_mcp_server.page.fill.assert_called_once_with(SELECTOR, TEXT_TO_FILL)
    assert f"Text '{TEXT_TO_FILL}' filled into element {SELECTOR} successfully." in result

def test_fill_element_no_page(mock_mcp_server_no_page):
    result = element_tools.fill_element(mock_mcp_server_no_page, SELECTOR, TEXT_TO_FILL)
    assert "Error: Page not initialized." in result

def test_fill_element_timeout_error(mock_mcp_server):
    mock_mcp_server.page.fill.side_effect = PlaywrightTimeoutError("Timeout filling")
    result = element_tools.fill_element(mock_mcp_server, SELECTOR, TEXT_TO_FILL)
    assert f"Timeout error filling element {SELECTOR}" in result

def test_fill_element_playwright_error(mock_mcp_server):
    mock_mcp_server.page.fill.side_effect = PlaywrightError("Generic Playwright error filling")
    result = element_tools.fill_element(mock_mcp_server, SELECTOR, TEXT_TO_FILL)
    assert f"Playwright error filling element {SELECTOR}: Generic Playwright error filling" in result

# Tests for capture_elements
def test_capture_elements_success(mock_mcp_server):
    mock_element1 = MagicMock()
    mock_element1.inner_text.return_value = "Text 1"
    mock_element1.inner_html.return_value = "<p>Html 1</p>"
    mock_element1.evaluate_handle.return_value.json_value.return_value = [{'name': 'class', 'value': 'btn'}]

    mock_element2 = MagicMock()
    mock_element2.inner_text.return_value = "Text 2"
    mock_element2.inner_html.return_value = "<div>Html 2</div>"
    mock_element2.evaluate_handle.return_value.json_value.return_value = [{'name': 'id', 'value': 'el2'}]

    mock_mcp_server.page.query_selector_all.return_value = [mock_element1, mock_element2]
    
    result = element_tools.capture_elements(mock_mcp_server, SELECTOR)
    
    mock_mcp_server.page.query_selector_all.assert_called_once_with(SELECTOR)
    assert len(result) == 2
    assert result[0]['innerText'] == "Text 1"
    assert result[0]['innerHTML'] == "<p>Html 1</p>"
    assert result[0]['attributes'] == {'class': 'btn'}
    assert result[1]['innerText'] == "Text 2"
    mock_element1.evaluate_handle.assert_called_once_with('el => Array.from(el.attributes).map(attr => ({name: attr.name, value: attr.value}))')

def test_capture_elements_no_elements_found(mock_mcp_server):
    mock_mcp_server.page.query_selector_all.return_value = []
    result = element_tools.capture_elements(mock_mcp_server, SELECTOR)
    assert f"No elements found matching selector: {SELECTOR}" in result

def test_capture_elements_no_page(mock_mcp_server_no_page):
    result = element_tools.capture_elements(mock_mcp_server_no_page, SELECTOR)
    assert "Error: Page not initialized." in result

def test_capture_elements_playwright_error(mock_mcp_server):
    mock_mcp_server.page.query_selector_all.side_effect = PlaywrightError("Query error")
    result = element_tools.capture_elements(mock_mcp_server, SELECTOR)
    assert f"Playwright error capturing elements with selector {SELECTOR}: Query error" in result

# Tests for evaluate_element
def test_evaluate_element_success(mock_mcp_server):
    mock_element = MagicMock()
    mock_element.evaluate.return_value = "evaluated_value"
    mock_mcp_server.page.query_selector.return_value = mock_element

    result = element_tools.evaluate_element(mock_mcp_server, SELECTOR, EXPRESSION)
    
    mock_mcp_server.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.evaluate.assert_called_once_with(EXPRESSION)
    assert result == "evaluated_value"

def test_evaluate_element_no_element_found(mock_mcp_server):
    mock_mcp_server.page.query_selector.return_value = None
    result = element_tools.evaluate_element(mock_mcp_server, SELECTOR, EXPRESSION)
    assert f"Error: Element not found for selector: {SELECTOR}" in result

def test_evaluate_element_no_page(mock_mcp_server_no_page):
    result = element_tools.evaluate_element(mock_mcp_server_no_page, SELECTOR, EXPRESSION)
    assert "Error: Page not initialized." in result

def test_evaluate_element_playwright_error(mock_mcp_server):
    mock_element = MagicMock()
    mock_element.evaluate.side_effect = PlaywrightError("Evaluation error")
    mock_mcp_server.page.query_selector.return_value = mock_element
    result = element_tools.evaluate_element(mock_mcp_server, SELECTOR, EXPRESSION)
    assert f"Playwright error evaluating expression '{EXPRESSION}' on element {SELECTOR}: Evaluation error" in result

def test_evaluate_element_evaluation_js_error(mock_mcp_server):
    # This test implies that the user-provided JS expression itself causes an error
    mock_element = MagicMock()
    # Playwright's evaluate might raise a generic PlaywrightError or a more specific one if the JS fails
    mock_element.evaluate.side_effect = PlaywrightError("JS execution failed in evaluate")
    mock_mcp_server.page.query_selector.return_value = mock_element
    result = element_tools.evaluate_element(mock_mcp_server, SELECTOR, "invalid js expression")
    assert "Playwright error evaluating expression" in result

# Tests for get_element_attribute
def test_get_element_attribute_success(mock_mcp_server):
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "test-value"
    mock_mcp_server.page.query_selector.return_value = mock_element

    result = element_tools.get_element_attribute(mock_mcp_server, SELECTOR, ATTRIBUTE_NAME)
    
    mock_mcp_server.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.get_attribute.assert_called_once_with(ATTRIBUTE_NAME)
    assert result == "test-value"

def test_get_element_attribute_not_found(mock_mcp_server):
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = None # Attribute does not exist
    mock_mcp_server.page.query_selector.return_value = mock_element
    result = element_tools.get_element_attribute(mock_mcp_server, SELECTOR, "nonexistent-attr")
    assert f"Attribute 'nonexistent-attr' not found for element {SELECTOR}" in result

def test_get_element_attribute_element_not_found(mock_mcp_server):
    mock_mcp_server.page.query_selector.return_value = None
    result = element_tools.get_element_attribute(mock_mcp_server, SELECTOR, ATTRIBUTE_NAME)
    assert f"Error: Element not found for selector: {SELECTOR}" in result

def test_get_element_attribute_no_page(mock_mcp_server_no_page):
    result = element_tools.get_element_attribute(mock_mcp_server_no_page, SELECTOR, ATTRIBUTE_NAME)
    assert "Error: Page not initialized." in result

def test_get_element_attribute_playwright_error(mock_mcp_server):
    mock_element = MagicMock()
    mock_element.get_attribute.side_effect = PlaywrightError("Get attribute error")
    mock_mcp_server.page.query_selector.return_value = mock_element
    result = element_tools.get_element_attribute(mock_mcp_server, SELECTOR, ATTRIBUTE_NAME)
    assert f"Playwright error getting attribute '{ATTRIBUTE_NAME}' for element {SELECTOR}: Get attribute error" in result

# Tests for get_text_content
def test_get_text_content_success(mock_mcp_server):
    mock_element = MagicMock()
    mock_element.text_content.return_value = "Expected Text"
    mock_mcp_server.page.query_selector.return_value = mock_element

    result = element_tools.get_text_content(mock_mcp_server, SELECTOR)
    
    mock_mcp_server.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.text_content.assert_called_once()
    assert result == "Expected Text"

def test_get_text_content_element_not_found(mock_mcp_server):
    mock_mcp_server.page.query_selector.return_value = None
    result = element_tools.get_text_content(mock_mcp_server, SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result

def test_get_text_content_no_page(mock_mcp_server_no_page):
    result = element_tools.get_text_content(mock_mcp_server_no_page, SELECTOR)
    assert "Error: Page not initialized." in result

def test_get_text_content_playwright_error(mock_mcp_server):
    mock_element = MagicMock()
    mock_element.text_content.side_effect = PlaywrightError("Get text error")
    mock_mcp_server.page.query_selector.return_value = mock_element
    result = element_tools.get_text_content(mock_mcp_server, SELECTOR)
    assert f"Playwright error getting text content for element {SELECTOR}: Get text error" in result

# Tests for wait_for_selector
def test_wait_for_selector_success(mock_mcp_server):
    result = element_tools.wait_for_selector(mock_mcp_server, SELECTOR, TIMEOUT_MS)
    mock_mcp_server.page.wait_for_selector.assert_called_once_with(SELECTOR, timeout=float(TIMEOUT_MS))
    assert f"Element {SELECTOR} found." in result

def test_wait_for_selector_no_page(mock_mcp_server_no_page):
    result = element_tools.wait_for_selector(mock_mcp_server_no_page, SELECTOR, TIMEOUT_MS)
    assert "Error: Page not initialized." in result

def test_wait_for_selector_timeout_error(mock_mcp_server):
    mock_mcp_server.page.wait_for_selector.side_effect = PlaywrightTimeoutError("Timeout waiting for selector")
    result = element_tools.wait_for_selector(mock_mcp_server, SELECTOR, TIMEOUT_MS)
    assert f"Timeout waiting for element {SELECTOR}." in result

def test_wait_for_selector_playwright_error(mock_mcp_server):
    mock_mcp_server.page.wait_for_selector.side_effect = PlaywrightError("Generic Playwright wait error")
    result = element_tools.wait_for_selector(mock_mcp_server, SELECTOR, TIMEOUT_MS)
    assert f"Playwright error waiting for selector {SELECTOR}: Generic Playwright wait error" in result
