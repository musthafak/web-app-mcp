"""Tests for element interaction tools in ToolManager."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, ANY

# Import Page for spec
from playwright.async_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    Page
)
from mcp_server.tool_manager import ToolManager


@pytest.fixture
def tool_manager_with_page():
    """Provides a ToolManager instance with a mocked page."""
    tm = ToolManager()
    tm.page = AsyncMock(spec=Page)
    # Key fix: Ensure the mocked page is not considered closed by default
    tm.page.is_closed.return_value = False
    return tm


@pytest.fixture
def tool_manager_no_page():
    """Provides a ToolManager instance where page is initially None."""
    tm = ToolManager()
    return tm


# Common variables
SELECTOR = "button.submit"
TEXT_TO_FILL = "hello world"
EXPRESSION = "element => element.value"
ATTRIBUTE_NAME = "data-testid"
TIMEOUT_MS = 15000


# Tests for click_element
@pytest.mark.asyncio
async def test_click_element_success(tool_manager_with_page):
    """Test successful element click."""
    result = await tool_manager_with_page.click_element(SELECTOR)
    tool_manager_with_page.page.click.assert_called_once_with(SELECTOR, timeout=3000)
    assert f"Element {SELECTOR} clicked successfully." in result


@pytest.mark.asyncio
async def test_click_element_no_page(tool_manager_no_page):
    """Test element click when page is not initialized."""
    result = await tool_manager_no_page.click_element(SELECTOR)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_click_element_timeout_error(tool_manager_with_page):
    """Test timeout error during element click."""
    tool_manager_with_page.page.click.side_effect = \
        PlaywrightTimeoutError("Timeout clicking")
    result = await tool_manager_with_page.click_element(SELECTOR)
    assert f"Timeout clicking {SELECTOR}. " \
           "Element may not be visible or interactable." in result


@pytest.mark.asyncio
async def test_click_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element click."""
    tool_manager_with_page.page.click.side_effect = \
        PlaywrightError("Generic Playwright error")
    result = await tool_manager_with_page.click_element(SELECTOR)
    assert f"PWE clicking {SELECTOR}: Generic Playwright error" in result


# Tests for fill_element
@pytest.mark.asyncio
async def test_fill_element_success(tool_manager_with_page):
    """Test successful element fill."""
    result = await tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    tool_manager_with_page.page.fill.assert_called_once_with(
        SELECTOR, TEXT_TO_FILL, timeout=3000)
    assert f"Text '{TEXT_TO_FILL}' filled into element " \
           f"{SELECTOR} successfully." in result


@pytest.mark.asyncio
async def test_fill_element_no_page(tool_manager_no_page):
    """Test element fill when page is not initialized."""
    result = await tool_manager_no_page.fill_element(SELECTOR, TEXT_TO_FILL)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_fill_element_timeout_error(tool_manager_with_page):
    """Test timeout error during element fill."""
    tool_manager_with_page.page.fill.side_effect = \
        PlaywrightTimeoutError("Timeout filling")
    result = await tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    assert f"Timeout filling {SELECTOR}. " \
           "Element may not be visible or an input field." in result


@pytest.mark.asyncio
async def test_fill_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element fill."""
    tool_manager_with_page.page.fill.side_effect = \
        PlaywrightError("Generic Playwright error filling")
    result = await tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    assert "PWE filling " \
           f"{SELECTOR}: Generic Playwright error filling" in result


# Tests for capture_elements
@pytest.mark.asyncio
async def test_capture_elements_success(tool_manager_with_page):
    """Test successful element capture."""
    mock_element1 = AsyncMock()
    mock_element1.inner_text.return_value = "Text 1"
    mock_element1.inner_html.return_value = "<p>Html 1</p>"
    mock_element1.evaluate_handle.return_value.json_value.return_value = \
        [{'name': 'class', 'value': 'btn'}]

    mock_element2 = AsyncMock()
    mock_element2.inner_text.return_value = "Text 2"
    mock_element2.inner_html.return_value = "<div>Html 2</div>"
    mock_element2.evaluate_handle.return_value.json_value.return_value = \
        [{'name': 'id', 'value': 'el2'}]

    tool_manager_with_page.page.query_selector_all.return_value = \
        [mock_element1, mock_element2]
    result = await tool_manager_with_page.capture_elements(SELECTOR)
    tool_manager_with_page.page.query_selector_all.assert_called_once_with(
        SELECTOR)
    assert len(result) == 2
    assert result[0]['innerText'] == "Text 1"
    assert result[0]['innerHTML'] == "<p>Html 1</p>"
    assert result[0]['attributes'] == {'class': 'btn'}
    assert result[1]['innerText'] == "Text 2"
    mock_element1.evaluate_handle.assert_called_once_with(
        'el => Array.from(el.attributes)'
        '.map(attr => ({name: attr.name, value: attr.value}))')


@pytest.mark.asyncio
async def test_capture_elements_no_elements_found(tool_manager_with_page):
    """Test element capture when no elements are found."""
    tool_manager_with_page.page.query_selector_all.return_value = []
    result = await tool_manager_with_page.capture_elements(SELECTOR)
    assert f"No elements found matching selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_capture_elements_no_page(tool_manager_no_page):
    """Test element capture when page is not initialized."""
    result = await tool_manager_no_page.capture_elements(SELECTOR)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_capture_elements_playwright_error(tool_manager_with_page):
    """Test Playwright error during element capture."""
    tool_manager_with_page.page.query_selector_all.side_effect = \
        PlaywrightError("Query error")
    result = await tool_manager_with_page.capture_elements(SELECTOR)
    assert f"PWE capturing elements for {SELECTOR}: Query error" in result


# Tests for evaluate_element
@pytest.mark.asyncio
async def test_evaluate_element_success(tool_manager_with_page):
    """Test successful element evaluation."""
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = "evaluated_value"
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.evaluate_element(SELECTOR, EXPRESSION)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.evaluate.assert_called_once_with(EXPRESSION)
    assert result == "evaluated_value"


@pytest.mark.asyncio
async def test_evaluate_element_no_element_found(tool_manager_with_page):
    """Test element evaluation when no element is found."""
    tool_manager_with_page.page.query_selector.return_value = None
    result = await tool_manager_with_page.evaluate_element(SELECTOR, EXPRESSION)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_evaluate_element_no_page(tool_manager_no_page):
    """Test element evaluation when page is not initialized."""
    result = await tool_manager_no_page.evaluate_element(SELECTOR, EXPRESSION)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_evaluate_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element evaluation."""
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = PlaywrightError("Evaluation error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.evaluate_element(SELECTOR, EXPRESSION)
    assert f"PWE evaluating expr '{EXPRESSION}' on " \
           f"{SELECTOR}: Evaluation error" in result


@pytest.mark.asyncio
async def test_evaluate_element_evaluation_js_error(tool_manager_with_page):
    """Test JavaScript error during element evaluation."""
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = \
        PlaywrightError("JS execution failed in evaluate")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.evaluate_element(
        SELECTOR, "invalid js expression")
    assert "PWE evaluating expr 'invalid js expression' on" in result


# Tests for get_element_attribute
@pytest.mark.asyncio
async def test_get_element_attribute_success(tool_manager_with_page):
    """Test successful retrieval of an element attribute."""
    mock_element = AsyncMock()
    mock_element.get_attribute.return_value = "test-value"
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.get_attribute.assert_called_once_with(ATTRIBUTE_NAME)
    assert result == "test-value"


@pytest.mark.asyncio
async def test_get_element_attribute_not_found(tool_manager_with_page):
    """Test retrieval of a non-existent element attribute."""
    mock_element = AsyncMock()
    mock_element.get_attribute.return_value = None
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_element_attribute(
        SELECTOR, "nonexistent-attr")
    assert "Attribute 'nonexistent-attr' not found for element " \
           f"{SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_attribute_element_not_found(tool_manager_with_page):
    """Test attribute retrieval when element is not found."""
    tool_manager_with_page.page.query_selector.return_value = None
    result = await tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_attribute_no_page(tool_manager_no_page):
    """Test attribute retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_get_element_attribute_playwright_error(tool_manager_with_page):
    """Test Playwright error during attribute retrieval."""
    mock_element = AsyncMock()
    mock_element.get_attribute.side_effect = \
        PlaywrightError("Get attribute error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert f"PWE getting attr '{ATTRIBUTE_NAME}' for " \
           f"{SELECTOR}: Get attribute error" in result


# Tests for get_text_content
@pytest.mark.asyncio
async def test_get_text_content_success(tool_manager_with_page):
    """Test successful retrieval of text content."""
    mock_element = AsyncMock()
    mock_element.text_content.return_value = "Expected Text"
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_text_content(SELECTOR)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.text_content.assert_called_once()
    assert result == "Expected Text"


@pytest.mark.asyncio
async def test_get_text_content_element_not_found(tool_manager_with_page):
    """Test text content retrieval when element is not found."""
    tool_manager_with_page.page.query_selector.return_value = None
    result = await tool_manager_with_page.get_text_content(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_text_content_no_page(tool_manager_no_page):
    """Test text content retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_text_content(SELECTOR)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_get_text_content_playwright_error(tool_manager_with_page):
    """Test Playwright error during text content retrieval."""
    mock_element = AsyncMock()
    mock_element.text_content.side_effect = PlaywrightError("Get text error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_text_content(SELECTOR)
    assert f"PWE getting text for {SELECTOR}: Get text error" in result


# Tests for wait_for_selector
@pytest.mark.asyncio
async def test_wait_for_selector_success(tool_manager_with_page):
    """Test successful waiting for a selector."""
    result = await tool_manager_with_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    tool_manager_with_page.page.wait_for_selector.assert_called_once_with(
        SELECTOR, timeout=float(TIMEOUT_MS))
    assert f"Element {SELECTOR} found." in result


@pytest.mark.asyncio
async def test_wait_for_selector_no_page(tool_manager_no_page):
    """Test waiting for selector when page is not initialized."""
    result = await tool_manager_no_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_wait_for_selector_timeout_error(tool_manager_with_page):
    """Test timeout error while waiting for a selector."""
    tool_manager_with_page.page.wait_for_selector.side_effect = \
        PlaywrightTimeoutError("Timeout waiting for selector")
    result = await tool_manager_with_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    assert f"Timeout waiting for element {SELECTOR}." in result


@pytest.mark.asyncio
async def test_wait_for_selector_playwright_error(tool_manager_with_page):
    """Test Playwright error while waiting for a selector."""
    tool_manager_with_page.page.wait_for_selector.side_effect = \
        PlaywrightError("Generic Playwright wait error")
    result = await tool_manager_with_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    assert "PWE waiting for " \
           f"{SELECTOR}: Generic Playwright wait error" in result


# Tests for hover_element
@pytest.mark.asyncio
async def test_hover_element_success(tool_manager_with_page):
    """Test successful element hover."""
    # Mock the element that query_selector will return
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.hover_element(SELECTOR)

    # Assert that query_selector was called to find the element
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)

    # Assert that hover was called on the mock_element
    mock_element.hover.assert_called_once_with(timeout=3000)

    # Assert the correct success message from tool_manager.py
    assert f"Successfully hovered over element {SELECTOR}." in result


@pytest.mark.asyncio
async def test_hover_element_no_page(tool_manager_no_page):
    """Test element hover when page is not initialized."""
    result = await tool_manager_no_page.hover_element(SELECTOR)
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_hover_element_timeout_error(tool_manager_with_page):
    """Test timeout error during element hover."""
    # Mock the element that query_selector will return
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element
    # Make the element's hover method raise the timeout error
    mock_element.hover.side_effect = PlaywrightTimeoutError("Timeout hovering")

    result = await tool_manager_with_page.hover_element(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.hover.assert_called_once_with(timeout=3000)
    # Assert the correct error message from tool_manager.py
    assert (f"Timeout hovering over {SELECTOR}. Element may not be "
            "visible or interactable for hover.") in result


@pytest.mark.asyncio
async def test_hover_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element hover."""
    # Mock the element that query_selector will return
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element
    # Make the element's hover method raise the Playwright error
    mock_element.hover.side_effect = PlaywrightError("Generic Playwright error")

    result = await tool_manager_with_page.hover_element(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.hover.assert_called_once_with(timeout=3000)
    # Assert the correct error message from tool_manager.py
    assert f"Playwright error hovering over {SELECTOR}: Generic Playwright error" in result


@pytest.mark.asyncio
async def test_hover_element_page_closed(tool_manager_with_page):
    """Test element hover when page is closed."""
    # This test specifically checks the case where page.is_closed() is True
    tool_manager_with_page.page.is_closed.return_value = True
    # query_selector should not be called if page is closed
    tool_manager_with_page.page.query_selector.return_value = None # Does not matter as it shouldn't be called

    result = await tool_manager_with_page.hover_element(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_not_called()
    # Assert the correct error message from tool_manager.py
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result


# Tests for select_option
@pytest.mark.asyncio
async def test_select_option_success_by_value(tool_manager_with_page):
    """Test successful option selection by value."""
    # Mock the element that query_selector will return
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element
    # Mock the select_option call on the element
    mock_element.select_option.return_value = ["value1"]

    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")

    # Assert that query_selector was called to find the element
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    # Assert that select_option was called on the mock_element
    mock_element.select_option.assert_called_once_with({"value": "value1"}, timeout=5000)
    # Assert the correct success message from tool_manager.py
    assert f"Successfully selected option(s) with value(s): ['value1'] for element {SELECTOR} using value 'value1'." in result


@pytest.mark.asyncio
async def test_select_option_success_by_label(tool_manager_with_page):
    """Test successful option selection by label."""
    # Mock the element that query_selector will return
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element
    # Mock the select_option call on the element
    mock_element.select_option.return_value = ["Label One"]

    result = await tool_manager_with_page.select_option(
        SELECTOR, option_label="Label One")

    # Assert that query_selector was called to find the element
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    # Assert that select_option was called on the mock_element
    mock_element.select_option.assert_called_once_with({"label": "Label One"}, timeout=5000)
    # Assert the correct success message from tool_manager.py
    assert f"Successfully selected option(s) with value(s): ['Label One'] for element {SELECTOR} using label 'Label One'." in result


@pytest.mark.asyncio
async def test_select_option_success_by_index(tool_manager_with_page):
    """Test successful option selection by index."""
    # Mock the element that query_selector will return
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element
    # Mock the select_option call on the element
    mock_element.select_option.return_value = ["1"]  # Playwright returns string value

    result = await tool_manager_with_page.select_option(SELECTOR, option_index=1)

    # Assert that query_selector was called to find the element
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    # Assert that select_option was called on the mock_element
    mock_element.select_option.assert_called_once_with({"index": 1}, timeout=5000)
    # Assert the correct success message from tool_manager.py
    assert f"Successfully selected option(s) with value(s): ['1'] for element {SELECTOR} using index 1." in result


@pytest.mark.asyncio
async def test_select_option_element_not_found(tool_manager_with_page):
    """Test option selection when the select element is not found."""
    # This test is for when the SELECTOR itself is not found.
    tool_manager_with_page.page.query_selector.return_value = None # Element not found

    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    # select_option on the element should not be called if element is None
    # tool_manager_with_page.page.select_option.assert_not_called() #This was for old logic
    assert f"Error: Select element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_select_option_option_not_found(tool_manager_with_page):
    """Test option selection when the specified option is not found."""
    # Element is found
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element
    # Simulate Playwright's element.select_option returning an empty list when option not found
    mock_element.select_option.return_value = []

    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="nonexistent")

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.select_option.assert_called_once_with({"value": "nonexistent"}, timeout=5000)
    # Check against the actual error message from tool_manager.py
    assert (f"Error: Could not select option using value 'nonexistent' "
            f"for element {SELECTOR}. Option may not exist or match.") in result


@pytest.mark.asyncio
async def test_select_option_no_specifier(tool_manager_with_page):
    """Test option selection when no option specifier is provided."""
    result = await tool_manager_with_page.select_option(SELECTOR)
    # Assert the correct error message from tool_manager.py
    assert "Error: No option specifier provided. Use option_value, option_label, or option_index." in result
    tool_manager_with_page.page.select_option.assert_not_called()


@pytest.mark.asyncio
async def test_select_option_multiple_specifiers(tool_manager_with_page):
    """Test option selection when multiple option specifiers are provided."""
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1", option_label="Label One")
    # Assert the correct error message from tool_manager.py
    assert "Error: Multiple option specifiers provided. Only one of option_value, option_label, or option_index should be used." in result
    tool_manager_with_page.page.select_option.assert_not_called()


@pytest.mark.asyncio
async def test_select_option_no_page(tool_manager_no_page):
    """Test option selection when page is not initialized."""
    result = await tool_manager_no_page.select_option(
        SELECTOR, option_value="value1")
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_select_option_playwright_error(tool_manager_with_page):
    """Test Playwright error during option selection."""
    # Mock the element that query_selector will return
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector.return_value = mock_element
    # Make the element's select_option method raise the Playwright error
    mock_element.select_option.side_effect = PlaywrightError("Generic Playwright error")

    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.select_option.assert_called_once_with({"value": "value1"}, timeout=5000)
    # Check against the actual error message from tool_manager.py
    assert (f"Playwright error selecting option for {SELECTOR} using value 'value1': "
            "Generic Playwright error") in result


@pytest.mark.asyncio
async def test_select_option_page_closed(tool_manager_with_page):
    """Test option selection when page is closed."""
    # This test specifically checks the case where page.is_closed() is True
    tool_manager_with_page.page.is_closed.return_value = True
    tool_manager_with_page.page.query_selector.return_value = None # Should not be called

    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")

    tool_manager_with_page.page.query_selector.assert_not_called()
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result


# Tests for get_element_html
@pytest.mark.asyncio
async def test_get_element_html_success(tool_manager_with_page):
    """Test successful retrieval of element's outerHTML."""
    mock_element = AsyncMock()
    # Mock the evaluate call on the element that gets the outerHTML
    mock_element.evaluate.return_value = "<p>Hello</p>"
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_html(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    # Expect one call to element.evaluate for "el => el.outerHTML"
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")
    assert result == "<p>Hello</p>"


@pytest.mark.asyncio
async def test_get_element_html_with_char_limit(tool_manager_with_page):
    """Test retrieval of element's outerHTML with character limit."""
    mock_element = AsyncMock()
    long_html = "<div><span>This is a very long HTML content that should be truncated.</span></div>"
    # Mock the evaluate call on the element that gets the outerHTML
    mock_element.evaluate.return_value = long_html
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_html(SELECTOR, char_limit=20)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")
    assert result == long_html[:20] + "..."


HTML_WITH_SCRIPTS_COMMENTS_STYLES = """
<div>
    <!-- This is a comment -->
    <p>Some text</p>
    <script>console.log("script content");</script>
    <style>.my-class { color: red; }</style>
    <link rel="stylesheet" href="styles.css">
</div>
"""

CLEANED_HTML_NO_SCRIPTS = """
<div>
    <!-- This is a comment -->
    <p>Some text</p>
    
    <style>.my-class { color: red; }</style>
    <link rel="stylesheet" href="styles.css">
</div>
"""

CLEANED_HTML_NO_COMMENTS = """
<div>
    
    <p>Some text</p>
    <script>console.log("script content");</script>
    <style>.my-class { color: red; }</style>
    <link rel="stylesheet" href="styles.css">
</div>
"""

CLEANED_HTML_NO_STYLES = """
<div>
    <!-- This is a comment -->
    <p>Some text</p>
    <script>console.log("script content");</script>
    
    
</div>
"""

CLEANED_HTML_NO_SCRIPTS_COMMENTS = """
<div>
    
    <p>Some text</p>
    
    <style>.my-class { color: red; }</style>
    <link rel="stylesheet" href="styles.css">
</div>
"""


@pytest.mark.asyncio
async def test_get_element_html_remove_scripts(tool_manager_with_page):
    """Test get_element_html with remove_scripts=True."""
    mock_element = AsyncMock()
    mock_element = AsyncMock()
    # Mock the initial HTML content that BeautifulSoup will process
    mock_element.evaluate.return_value = HTML_WITH_SCRIPTS_COMMENTS_STYLES 
    tool_manager_with_page.page.query_selector.return_value = mock_element

    # We need to patch BeautifulSoup since it's called internally
    with patch('mcp_server.tool_manager.BeautifulSoup') as mock_bs:
        # Configure the mock BeautifulSoup instance that will be created
        mock_soup_instance = MagicMock()
        
        # Simulate finding script tags
        mock_script_tag = MagicMock()
        mock_script_tag.name = "script" # For verification if needed
        # mock_script_tag.decompose should be a mock itself to allow assertions
        mock_script_tag.decompose = MagicMock()
        
        # find_all for 'script' should return a list containing our mock_script_tag
        # find_all for other things (like comments or styles if they were also removed) would be different
        def find_all_side_effect(tag_name, **kwargs):
            if tag_name == 'script':
                return [mock_script_tag]
            return [] # Default for other tags if any were queried by mistake
        mock_soup_instance.find_all.side_effect = find_all_side_effect

        # Configure __str__ to return the cleaned HTML
        mock_soup_instance.__str__.return_value = CLEANED_HTML_NO_SCRIPTS.strip()
        mock_bs.return_value = mock_soup_instance # When BeautifulSoup() is called, return our mock_soup_instance

        result = await tool_manager_with_page.get_element_html(
            SELECTOR, remove_scripts=True
        )

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    # element.evaluate is called once to get the initial HTML for BeautifulSoup
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")
    
    # Check that BeautifulSoup was called with the raw HTML
    mock_bs.assert_called_once_with(HTML_WITH_SCRIPTS_COMMENTS_STYLES, "html.parser")
    
    # Check that find_all was called on the soup to find 'script' tags
    mock_soup_instance.find_all.assert_any_call("script")
    # Check that decompose was called on the mock script tag
    mock_script_tag.decompose.assert_called_once()
    
    assert result == CLEANED_HTML_NO_SCRIPTS.strip()


@pytest.mark.asyncio
async def test_get_element_html_remove_comments(tool_manager_with_page):
    """Test get_element_html with remove_comments=True."""
    mock_element = AsyncMock()
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = HTML_WITH_SCRIPTS_COMMENTS_STYLES
    tool_manager_with_page.page.query_selector.return_value = mock_element

    class DummyCommentTypeForTest: # Helper class for isinstance check
        pass

    with patch('mcp_server.tool_manager.BeautifulSoup') as mock_bs, \
         patch('mcp_server.tool_manager.Comment', DummyCommentTypeForTest) as MockCommentTypeInPatchAttheTestLevel:

        mock_soup_instance = MagicMock()
        
        # Simulate finding comment nodes
        # This node will be checked by `isinstance(mock_comment_node, Comment)`
        # where Comment is now DummyCommentTypeForTest
        mock_comment_node = DummyCommentTypeForTest() 
        # Add extract capability to our dummy instance
        mock_comment_node.extract = MagicMock()

        def find_all_side_effect_comments(string):
            # Check if the provided 'string' argument is a callable (lambda)
            if callable(string):
                # The lambda in tool_manager.py is `lambda text: isinstance(text, Comment)`
                # Comment is now DummyCommentTypeForTest.
                # So, we call the lambda with our mock_comment_node.
                if string(mock_comment_node): 
                    return [mock_comment_node]
            return []
        
        mock_soup_instance.find_all.side_effect = find_all_side_effect_comments
        mock_soup_instance.__str__.return_value = CLEANED_HTML_NO_COMMENTS.strip()
        mock_bs.return_value = mock_soup_instance

        result = await tool_manager_with_page.get_element_html(
            SELECTOR, remove_comments=True
        )

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")
    mock_bs.assert_called_once_with(HTML_WITH_SCRIPTS_COMMENTS_STYLES, "html.parser")
    
    # Check that find_all was called with a callable (our lambda)
    mock_soup_instance.find_all.assert_called_once_with(string=ANY)
    assert callable(mock_soup_instance.find_all.call_args[1]['string'])

    # Check that extract was called on the mock comment node
    mock_comment_node.extract.assert_called_once()
    assert result == CLEANED_HTML_NO_COMMENTS.strip()


@pytest.mark.asyncio
async def test_get_element_html_remove_styles(tool_manager_with_page):
    """Test get_element_html with remove_styles=True."""
    mock_element = AsyncMock()
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = HTML_WITH_SCRIPTS_COMMENTS_STYLES
    tool_manager_with_page.page.query_selector.return_value = mock_element

    with patch('mcp_server.tool_manager.BeautifulSoup') as mock_bs:
        mock_soup_instance = MagicMock()
        
        mock_style_tag = MagicMock()
        mock_style_tag.decompose = MagicMock()
        mock_link_tag = MagicMock()
        mock_link_tag.decompose = MagicMock()

        def find_all_side_effect_styles(tag_name, rel=None, **kwargs):
            if tag_name == 'style':
                return [mock_style_tag]
            if tag_name == 'link' and rel == 'stylesheet':
                return [mock_link_tag]
            return []
        
        mock_soup_instance.find_all.side_effect = find_all_side_effect_styles
        mock_soup_instance.__str__.return_value = CLEANED_HTML_NO_STYLES.strip()
        mock_bs.return_value = mock_soup_instance

        result = await tool_manager_with_page.get_element_html(
            SELECTOR, remove_styles=True
        )

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")
    mock_bs.assert_called_once_with(HTML_WITH_SCRIPTS_COMMENTS_STYLES, "html.parser")
    
    mock_soup_instance.find_all.assert_any_call("style")
    mock_soup_instance.find_all.assert_any_call("link", rel="stylesheet")
    mock_style_tag.decompose.assert_called_once()
    mock_link_tag.decompose.assert_called_once()
    
    assert result == CLEANED_HTML_NO_STYLES.strip()


@pytest.mark.asyncio
async def test_get_element_html_remove_scripts_comments(tool_manager_with_page):
    """Test get_element_html with remove_scripts=True and remove_comments=True."""
    mock_element = AsyncMock()
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = HTML_WITH_SCRIPTS_COMMENTS_STYLES
    tool_manager_with_page.page.query_selector.return_value = mock_element

    class DummyCommentTypeForTest: pass

    with patch('mcp_server.tool_manager.BeautifulSoup') as mock_bs, \
         patch('mcp_server.tool_manager.Comment', DummyCommentTypeForTest) as MockCommentTypeInPatchAttheTestLevel:

        mock_soup_instance = MagicMock()
        
        mock_script_tag = MagicMock()
        mock_script_tag.decompose = MagicMock()
        
        mock_comment_node = DummyCommentTypeForTest()
        mock_comment_node.extract = MagicMock()

        def find_all_side_effect_scripts_comments(*args_call, **kwargs_call):
            name_arg = None
            if args_call:
                name_arg = args_call[0]
            # BeautifulSoup's find_all uses 'name' for the tag name if passed as a keyword.
            # However, it's more common to pass it as the first positional argument.
            # We also need to check for kwargs_call['name'] if bs4 passes it that way under some circumstances.
            # For this test, direct positional 'script' or keyword 'string' are the main concerns.

            if name_arg == 'script':
                return [mock_script_tag]
            
            string_arg = kwargs_call.get('string')
            if callable(string_arg): # For comments lambda
                if string_arg(mock_comment_node): # Call the lambda
                    return [mock_comment_node]
            return []
        
        mock_soup_instance.find_all.side_effect = find_all_side_effect_scripts_comments
        mock_soup_instance.__str__.return_value = CLEANED_HTML_NO_SCRIPTS_COMMENTS.strip()
        mock_bs.return_value = mock_soup_instance

        result = await tool_manager_with_page.get_element_html(
            SELECTOR, remove_scripts=True, remove_comments=True
        )

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")
    mock_bs.assert_called_once_with(HTML_WITH_SCRIPTS_COMMENTS_STYLES, "html.parser")
    
    mock_soup_instance.find_all.assert_any_call("script")
    mock_soup_instance.find_all.assert_any_call(string=ANY) # For comments
    assert callable(mock_soup_instance.find_all.call_args_list[1][1]['string']) # Check it was a lambda

    mock_script_tag.decompose.assert_called_once()
    mock_comment_node.extract.assert_called_once()
    
    assert result == CLEANED_HTML_NO_SCRIPTS_COMMENTS.strip()


@pytest.mark.asyncio
async def test_get_element_html_element_not_found(tool_manager_with_page):
    """Test get_element_html when element is not found."""
    tool_manager_with_page.page.query_selector.return_value = None # Element not found

    result = await tool_manager_with_page.get_element_html(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
        # If query_selector returns None, element.evaluate should not be reached.
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_html_no_page(tool_manager_no_page):
    """Test get_element_html when page is not initialized."""
    result = await tool_manager_no_page.get_element_html(SELECTOR)
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_get_element_html_playwright_error(tool_manager_with_page):
    """Test Playwright error during get_element_html."""
    # Case 1: query_selector raises an error
    tool_manager_with_page.page.query_selector.side_effect = PlaywrightError("Query selector error")
    
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    assert f"Playwright error getting HTML for {SELECTOR}: Query selector error" in result

    # Case 2: element.evaluate raises an error
    tool_manager_with_page.page.query_selector.reset_mock() # Reset for next scenario
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = PlaywrightError("Evaluate error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    tool_manager_with_page.page.query_selector.side_effect = None # Clear previous side_effect

    result_eval_error = await tool_manager_with_page.get_element_html(SELECTOR)
    
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")
    assert f"Playwright error getting HTML for {SELECTOR}: Evaluate error" in result_eval_error


@pytest.mark.asyncio
async def test_get_element_html_page_closed(tool_manager_with_page):
    """Test get_element_html when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    # query_selector should not be called if page is closed
    tool_manager_with_page.page.query_selector.return_value = None 

    result = await tool_manager_with_page.get_element_html(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_not_called()
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result


# Tests for get_element_bounding_box
@pytest.mark.asyncio
async def test_get_element_bounding_box_success(tool_manager_with_page):
    """Test successful retrieval of an element's bounding box."""
    mock_element = AsyncMock()
    expected_box = {"x": 10, "y": 20, "width": 100, "height": 50}
    mock_element = AsyncMock()
    expected_box = {"x": 10, "y": 20, "width": 100, "height": 50}
    mock_element.bounding_box.return_value = expected_box
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.bounding_box.assert_called_once()
    assert result == expected_box


@pytest.mark.asyncio
async def test_get_element_bounding_box_element_not_found(
        tool_manager_with_page):
    """Test bounding box retrieval when element is not found."""
    tool_manager_with_page.page.query_selector.return_value = None # Element not found

    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_not_visible(tool_manager_with_page):
    """Test bounding box retrieval for a non-visible element."""
    mock_element = AsyncMock()
    mock_element = AsyncMock()
    mock_element.bounding_box.return_value = None  # Non-visible elements have no box
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.bounding_box.assert_called_once()
    # Check against the actual error message from tool_manager.py
    assert (f"Error: Element {SELECTOR} found, but it is not visible or "
            "has no dimensions.") in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_no_page(tool_manager_no_page):
    """Test bounding box retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_element_bounding_box(SELECTOR)
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_playwright_error(
        tool_manager_with_page):
    """Test Playwright error during bounding box retrieval."""
    mock_element = AsyncMock()
    # Case 1: query_selector raises an error
    tool_manager_with_page.page.query_selector.side_effect = PlaywrightError("Query selector error")

    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    assert f"Playwright error getting bounding box for {SELECTOR}: Query selector error" in result

    # Case 2: element.bounding_box raises an error
    tool_manager_with_page.page.query_selector.reset_mock()
    mock_element = AsyncMock()
    mock_element.bounding_box.side_effect = PlaywrightError("Bounding box error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    tool_manager_with_page.page.query_selector.side_effect = None # Clear previous side_effect
    
    result_eval_error = await tool_manager_with_page.get_element_bounding_box(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    mock_element.bounding_box.assert_called_once()
    assert f"Playwright error getting bounding box for {SELECTOR}: Bounding box error" in result_eval_error


@pytest.mark.asyncio
async def test_get_element_bounding_box_page_closed(tool_manager_with_page):
    """Test bounding box retrieval when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    tool_manager_with_page.page.query_selector.return_value = None # Should not be called

    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)

    tool_manager_with_page.page.query_selector.assert_not_called()
    assert "Error: Page not initialized or has been closed. Call 'new_page' first." in result
