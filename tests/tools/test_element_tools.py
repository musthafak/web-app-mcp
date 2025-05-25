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
    result = await tool_manager_with_page.hover_element(SELECTOR)
    tool_manager_with_page.page.hover.assert_called_once_with(SELECTOR, timeout=3000)
    assert f"Element {SELECTOR} hovered successfully." in result


@pytest.mark.asyncio
async def test_hover_element_no_page(tool_manager_no_page):
    """Test element hover when page is not initialized."""
    result = await tool_manager_no_page.hover_element(SELECTOR)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_hover_element_timeout_error(tool_manager_with_page):
    """Test timeout error during element hover."""
    tool_manager_with_page.page.hover.side_effect = \
        PlaywrightTimeoutError("Timeout hovering")
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert f"Timeout hovering {SELECTOR}. " \
           "Element may not be visible or interactable." in result


@pytest.mark.asyncio
async def test_hover_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element hover."""
    tool_manager_with_page.page.hover.side_effect = \
        PlaywrightError("Generic Playwright error")
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert f"PWE hovering {SELECTOR}: Generic Playwright error" in result


@pytest.mark.asyncio
async def test_hover_element_page_closed(tool_manager_with_page):
    """Test element hover when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert "Error: Page is closed." in result


# Tests for select_option
@pytest.mark.asyncio
async def test_select_option_success_by_value(tool_manager_with_page):
    """Test successful option selection by value."""
    tool_manager_with_page.page.select_option.return_value = ["value1"]
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")
    tool_manager_with_page.page.select_option.assert_called_once_with(
        SELECTOR, value="value1", timeout=3000)
    assert f"Option with value 'value1' selected for element {SELECTOR}." in result


@pytest.mark.asyncio
async def test_select_option_success_by_label(tool_manager_with_page):
    """Test successful option selection by label."""
    tool_manager_with_page.page.select_option.return_value = ["Label One"]
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_label="Label One")
    tool_manager_with_page.page.select_option.assert_called_once_with(
        SELECTOR, label="Label One", timeout=3000)
    assert f"Option with label 'Label One' selected for element {SELECTOR}." in result


@pytest.mark.asyncio
async def test_select_option_success_by_index(tool_manager_with_page):
    """Test successful option selection by index."""
    tool_manager_with_page.page.select_option.return_value = ["1"] # Playwright returns string value
    result = await tool_manager_with_page.select_option(SELECTOR, option_index=1)
    tool_manager_with_page.page.select_option.assert_called_once_with(
        SELECTOR, index=1, timeout=3000)
    assert f"Option at index 1 selected for element {SELECTOR}." in result


@pytest.mark.asyncio
async def test_select_option_element_not_found(tool_manager_with_page):
    """Test option selection when the select element is not found."""
    tool_manager_with_page.page.select_option.side_effect = \
        PlaywrightTimeoutError("Timeout selecting option")
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")
    assert f"Timeout selecting option for {SELECTOR}. " \
           "Element not found or not a select element." in result


@pytest.mark.asyncio
async def test_select_option_option_not_found(tool_manager_with_page):
    """Test option selection when the specified option is not found."""
    # Simulate Playwright returning an empty list when option not found
    tool_manager_with_page.page.select_option.return_value = []
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="nonexistent")
    assert "Option 'nonexistent' (by value) not found for " \
           f"element {SELECTOR}." in result


@pytest.mark.asyncio
async def test_select_option_no_specifier(tool_manager_with_page):
    """Test option selection when no option specifier is provided."""
    result = await tool_manager_with_page.select_option(SELECTOR)
    assert "Error: Please provide an option specifier: " \
           "option_value, option_label, or option_index." in result
    tool_manager_with_page.page.select_option.assert_not_called()


@pytest.mark.asyncio
async def test_select_option_multiple_specifiers(tool_manager_with_page):
    """Test option selection when multiple option specifiers are provided."""
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1", option_label="Label One")
    assert "Error: Please provide only one option specifier." in result
    tool_manager_with_page.page.select_option.assert_not_called()


@pytest.mark.asyncio
async def test_select_option_no_page(tool_manager_no_page):
    """Test option selection when page is not initialized."""
    result = await tool_manager_no_page.select_option(
        SELECTOR, option_value="value1")
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_select_option_playwright_error(tool_manager_with_page):
    """Test Playwright error during option selection."""
    tool_manager_with_page.page.select_option.side_effect = \
        PlaywrightError("Generic Playwright error")
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")
    assert "PWE selecting option for " \
           f"{SELECTOR}: Generic Playwright error" in result


@pytest.mark.asyncio
async def test_select_option_page_closed(tool_manager_with_page):
    """Test option selection when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.select_option(
        SELECTOR, option_value="value1")
    assert "Error: Page is closed." in result


# Tests for get_element_html
@pytest.mark.asyncio
async def test_get_element_html_success(tool_manager_with_page):
    """Test successful retrieval of element's outerHTML."""
    mock_element = AsyncMock()
    mock_element.evaluate.return_value = "<p>Hello</p>"
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    # Expect two calls: one for remove_scripts, one for the actual HTML
    assert mock_element.evaluate.call_count == 2
    assert result == "<p>Hello</p>"


@pytest.mark.asyncio
async def test_get_element_html_with_char_limit(tool_manager_with_page):
    """Test retrieval of element's outerHTML with character limit."""
    mock_element = AsyncMock()
    long_html = "<div><span>This is a very long HTML content that should be truncated.</span></div>"
    mock_element.evaluate.return_value = long_html
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_element_html(SELECTOR, char_limit=20)
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
    # First evaluate call is for script removal, second is for the actual HTML
    mock_element.evaluate.side_effect = [None, CLEANED_HTML_NO_SCRIPTS.strip()]
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_html(
        SELECTOR, remove_scripts=True
    )
    tool_manager_with_page.page.query_selector.assert_called_once_with(SELECTOR)
    assert mock_element.evaluate.call_count == 2
    # First call to remove scripts
    mock_element.evaluate.assert_any_call(
        "el => { el.querySelectorAll('script').forEach(s => s.remove()); }"
    )
    # Second call to get outerHTML
    mock_element.evaluate.assert_any_call("el => el.outerHTML")
    assert result == CLEANED_HTML_NO_SCRIPTS.strip()


@pytest.mark.asyncio
async def test_get_element_html_remove_comments(tool_manager_with_page):
    """Test get_element_html with remove_comments=True."""
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = [None, CLEANED_HTML_NO_COMMENTS.strip()]
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_html(
        SELECTOR, remove_comments=True
    )
    assert mock_element.evaluate.call_count == 2
    mock_element.evaluate.assert_any_call(
        "el => { el.childNodes.forEach(c => { if (c.nodeType === Node.COMMENT_NODE) { c.remove(); } }); }"
    )
    mock_element.evaluate.assert_any_call("el => el.outerHTML")
    assert result == CLEANED_HTML_NO_COMMENTS.strip()


@pytest.mark.asyncio
async def test_get_element_html_remove_styles(tool_manager_with_page):
    """Test get_element_html with remove_styles=True."""
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = [None, None, CLEANED_HTML_NO_STYLES.strip()] # 2 for removal, 1 for result
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_html(
        SELECTOR, remove_styles=True
    )
    assert mock_element.evaluate.call_count == 3
    mock_element.evaluate.assert_any_call(
        "el => { el.querySelectorAll('style').forEach(s => s.remove()); }"
    )
    mock_element.evaluate.assert_any_call(
        "el => { el.querySelectorAll('link[rel=\"stylesheet\"]').forEach(l => l.remove()); }"
    )
    mock_element.evaluate.assert_any_call("el => el.outerHTML")
    assert result == CLEANED_HTML_NO_STYLES.strip()


@pytest.mark.asyncio
async def test_get_element_html_remove_scripts_comments(tool_manager_with_page):
    """Test get_element_html with remove_scripts=True and remove_comments=True."""
    mock_element = AsyncMock()
    # script removal, comment removal, then get HTML
    mock_element.evaluate.side_effect = [None, None, CLEANED_HTML_NO_SCRIPTS_COMMENTS.strip()]
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.get_element_html(
        SELECTOR, remove_scripts=True, remove_comments=True
    )
    assert mock_element.evaluate.call_count == 3
    mock_element.evaluate.assert_any_call(
        "el => { el.querySelectorAll('script').forEach(s => s.remove()); }"
    )
    mock_element.evaluate.assert_any_call(
        "el => { el.childNodes.forEach(c => { if (c.nodeType === Node.COMMENT_NODE) { c.remove(); } }); }"
    )
    mock_element.evaluate.assert_any_call("el => el.outerHTML")
    assert result == CLEANED_HTML_NO_SCRIPTS_COMMENTS.strip()


@pytest.mark.asyncio
async def test_get_element_html_element_not_found(tool_manager_with_page):
    """Test get_element_html when element is not found."""
    tool_manager_with_page.page.query_selector.return_value = None
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_html_no_page(tool_manager_no_page):
    """Test get_element_html when page is not initialized."""
    result = await tool_manager_no_page.get_element_html(SELECTOR)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_get_element_html_playwright_error(tool_manager_with_page):
    """Test Playwright error during get_element_html."""
    tool_manager_with_page.page.query_selector.side_effect = \
        PlaywrightError("Generic Playwright error")
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert "PWE getting HTML for " \
           f"{SELECTOR}: Generic Playwright error" in result


@pytest.mark.asyncio
async def test_get_element_html_page_closed(tool_manager_with_page):
    """Test get_element_html when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert "Error: Page is closed." in result


# Tests for get_element_bounding_box
@pytest.mark.asyncio
async def test_get_element_bounding_box_success(tool_manager_with_page):
    """Test successful retrieval of an element's bounding box."""
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
    tool_manager_with_page.page.query_selector.return_value = None
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_not_visible(tool_manager_with_page):
    """Test bounding box retrieval for a non-visible element."""
    mock_element = AsyncMock()
    mock_element.bounding_box.return_value = None  # Non-visible elements have no box
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert f"Element {SELECTOR} found, but has no bounding box " \
           "(e.g., not visible)." in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_no_page(tool_manager_no_page):
    """Test bounding box retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_element_bounding_box(SELECTOR)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_playwright_error(
        tool_manager_with_page):
    """Test Playwright error during bounding box retrieval."""
    mock_element = AsyncMock()
    mock_element.bounding_box.side_effect = \
        PlaywrightError("Bounding box error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert "PWE getting bounding box for " \
           f"{SELECTOR}: Bounding box error" in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_page_closed(tool_manager_with_page):
    """Test bounding box retrieval when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert "Error: Page is closed." in result
