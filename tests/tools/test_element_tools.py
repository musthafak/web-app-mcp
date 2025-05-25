"""Tests for element interaction tools in ToolManager."""
import pytest
from unittest.mock import AsyncMock, MagicMock

# Import Page for spec
from playwright.async_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    Page
)
from mcp_server.tool_manager import ToolManager


@pytest.fixture
async def tool_manager_with_page():
    """Provides a ToolManager instance with a mocked page."""
    tm = ToolManager()
    tm.page = AsyncMock(spec=Page)
    return tm


@pytest.fixture
async def tool_manager_no_page():
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
    tool_manager_with_page.page.click.assert_called_once_with(SELECTOR)
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


@pytest.mark.asyncio
async def test_click_element_generic_exception(tool_manager_with_page):
    """Test generic Exception during element click."""
    tool_manager_with_page.page.click.side_effect = \
        Exception("Generic click error")
    result = await tool_manager_with_page.click_element(SELECTOR)
    assert f"Error clicking {SELECTOR}: Generic click error" in result


# Tests for fill_element
@pytest.mark.asyncio
async def test_fill_element_success(tool_manager_with_page):
    """Test successful element fill."""
    result = await tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    tool_manager_with_page.page.fill.assert_called_once_with(
        SELECTOR, TEXT_TO_FILL)
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


@pytest.mark.asyncio
async def test_fill_element_generic_exception(tool_manager_with_page):
    """Test generic Exception during element fill."""
    tool_manager_with_page.page.fill.side_effect = \
        Exception("Generic fill error")
    result = await tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    assert f"Error filling {SELECTOR}: Generic fill error" in result


# Tests for capture_elements
@pytest.mark.asyncio
async def test_capture_elements_success(tool_manager_with_page):
    """Test successful element capture."""
    mock_element1 = AsyncMock()
    mock_element1.inner_text = AsyncMock(return_value="Text 1")
    mock_element1.inner_html = AsyncMock(return_value="<p>Html 1</p>")
    mock_element1.evaluate_handle.return_value.json_value = AsyncMock(
        return_value=[{'name': 'class', 'value': 'btn'}])

    mock_element2 = AsyncMock()
    mock_element2.inner_text = AsyncMock(return_value="Text 2")
    mock_element2.inner_html = AsyncMock(return_value="<div>Html 2</div>")
    mock_element2.evaluate_handle.return_value.json_value = AsyncMock(
        return_value=[{'name': 'id', 'value': 'el2'}])

    tool_manager_with_page.page.query_selector_all = AsyncMock(
        return_value=[mock_element1, mock_element2])
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
    tool_manager_with_page.page.query_selector_all = AsyncMock(return_value=[])
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


@pytest.mark.asyncio
async def test_capture_elements_generic_exception(tool_manager_with_page):
    """Test generic Exception during element capture."""
    tool_manager_with_page.page.query_selector_all.side_effect = \
        Exception("Generic query error")
    result = await tool_manager_with_page.capture_elements(SELECTOR)
    assert f"Error capturing elements for {SELECTOR}: Generic query error" \
           in result


# Tests for evaluate_element
@pytest.mark.asyncio
async def test_evaluate_element_success(tool_manager_with_page):
    """Test successful element evaluation."""
    mock_element = AsyncMock()
    mock_element.evaluate = AsyncMock(return_value="evaluated_value")
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.evaluate_element(
        SELECTOR, EXPRESSION)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.evaluate.assert_called_once_with(EXPRESSION)
    assert result == "evaluated_value"


@pytest.mark.asyncio
async def test_evaluate_element_no_element_found(tool_manager_with_page):
    """Test element evaluation when no element is found."""
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)
    result = await tool_manager_with_page.evaluate_element(
        SELECTOR, EXPRESSION)
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
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.evaluate_element(
        SELECTOR, EXPRESSION)
    assert f"PWE evaluating expr '{EXPRESSION}' on " \
           f"{SELECTOR}: Evaluation error" in result


@pytest.mark.asyncio
async def test_evaluate_element_evaluation_js_error(tool_manager_with_page):
    """Test JavaScript error during element evaluation."""
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = \
        PlaywrightError("JS execution failed in evaluate")
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.evaluate_element(
        SELECTOR, "invalid js expression")
    assert "PWE evaluating expr 'invalid js expression' on" in result


@pytest.mark.asyncio
async def test_evaluate_element_generic_exception(tool_manager_with_page):
    """Test generic Exception during element evaluation."""
    mock_element = AsyncMock()
    mock_element.evaluate.side_effect = Exception("Generic evaluation error")
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.evaluate_element(
        SELECTOR, EXPRESSION)
    assert f"Error evaluating expr '{EXPRESSION}' on " \
           f"{SELECTOR}: Generic evaluation error" in result


# Tests for get_element_attribute
@pytest.mark.asyncio
async def test_get_element_attribute_success(tool_manager_with_page):
    """Test successful retrieval of an element attribute."""
    mock_element = AsyncMock()
    mock_element.get_attribute = AsyncMock(return_value="test-value")
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
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
    mock_element.get_attribute = AsyncMock(return_value=None)
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.get_element_attribute(
        SELECTOR, "nonexistent-attr")
    assert "Attribute 'nonexistent-attr' not found for element " \
           f"{SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_attribute_element_not_found(
        tool_manager_with_page):
    """Test attribute retrieval when element is not found."""
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)
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
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert f"PWE getting attr '{ATTRIBUTE_NAME}' for " \
           f"{SELECTOR}: Get attribute error" in result


@pytest.mark.asyncio
async def test_get_element_attribute_generic_exception(tool_manager_with_page):
    """Test generic Exception during attribute retrieval."""
    mock_element = AsyncMock()
    mock_element.get_attribute.side_effect = \
        Exception("Generic get attribute error")
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert f"Error getting attr '{ATTRIBUTE_NAME}' for " \
           f"{SELECTOR}: Generic get attribute error" in result


# Tests for get_text_content
@pytest.mark.asyncio
async def test_get_text_content_success(tool_manager_with_page):
    """Test successful retrieval of text content."""
    mock_element = AsyncMock()
    mock_element.text_content = AsyncMock(return_value="Expected Text")
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.get_text_content(SELECTOR)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.text_content.assert_called_once()
    assert result == "Expected Text"


@pytest.mark.asyncio
async def test_get_text_content_element_not_found(tool_manager_with_page):
    """Test text content retrieval when element is not found."""
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)
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
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.get_text_content(SELECTOR)
    assert f"PWE getting text for {SELECTOR}: Get text error" in result


@pytest.mark.asyncio
async def test_get_text_content_generic_exception(tool_manager_with_page):
    """Test generic Exception during text content retrieval."""
    mock_element = AsyncMock()
    mock_element.text_content.side_effect = Exception("Generic get text error")
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    result = await tool_manager_with_page.get_text_content(SELECTOR)
    assert f"Error getting text for {SELECTOR}: Generic get text error" \
           in result


# Tests for wait_for_selector
@pytest.mark.asyncio
async def test_wait_for_selector_success(tool_manager_with_page):
    """Test successful waiting for a selector."""
    result = await tool_manager_with_page.wait_for_selector(
        SELECTOR, TIMEOUT_MS)
    tool_manager_with_page.page.wait_for_selector.assert_called_once_with(
        SELECTOR, timeout=float(TIMEOUT_MS))
    assert f"Element {SELECTOR} found." in result


@pytest.mark.asyncio
async def test_wait_for_selector_no_page(tool_manager_no_page):
    """Test waiting for selector when page is not initialized."""
    result = await tool_manager_no_page.wait_for_selector(
        SELECTOR, TIMEOUT_MS)
    assert "Error: Page not initialized." in result


@pytest.mark.asyncio
async def test_wait_for_selector_timeout_error(tool_manager_with_page):
    """Test timeout error while waiting for a selector."""
    tool_manager_with_page.page.wait_for_selector.side_effect = \
        PlaywrightTimeoutError("Timeout waiting for selector")
    result = await tool_manager_with_page.wait_for_selector(
        SELECTOR, TIMEOUT_MS)
    assert f"Timeout waiting for element {SELECTOR}." in result


@pytest.mark.asyncio
async def test_wait_for_selector_playwright_error(tool_manager_with_page):
    """Test Playwright error while waiting for a selector."""
    tool_manager_with_page.page.wait_for_selector.side_effect = \
        PlaywrightError("Generic Playwright wait error")
    result = await tool_manager_with_page.wait_for_selector(
        SELECTOR, TIMEOUT_MS)
    assert "PWE waiting for " \
           f"{SELECTOR}: Generic Playwright wait error" in result


@pytest.mark.asyncio
async def test_wait_for_selector_generic_exception(tool_manager_with_page):
    """Test generic Exception while waiting for a selector."""
    tool_manager_with_page.page.wait_for_selector.side_effect = \
        Exception("Generic wait error")
    result = await tool_manager_with_page.wait_for_selector(
        SELECTOR, TIMEOUT_MS)
    assert f"Error waiting for {SELECTOR}: Generic wait error" in result


# Tests for hover_element
@pytest.mark.asyncio
async def test_hover_element_success(tool_manager_with_page):
    """Test successful element hover."""
    mock_element = AsyncMock()
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.hover_element(SELECTOR)
    mock_element.hover.assert_called_once()
    assert f"Hovered over element {SELECTOR} successfully." in result


@pytest.mark.asyncio
async def test_hover_element_not_found(tool_manager_with_page):
    """Test hover when element is not found."""
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_hover_element_page_not_initialized(tool_manager_no_page):
    """Test hover when page is not initialized."""
    result = await tool_manager_no_page.hover_element(SELECTOR)
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_hover_element_page_closed(tool_manager_with_page):
    """Test hover when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_hover_element_timeout_error(tool_manager_with_page):
    """Test timeout error during hover."""
    mock_element = AsyncMock()
    mock_element.hover = AsyncMock(
        side_effect=PlaywrightTimeoutError("Timeout hovering"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert f"Timeout hovering over {SELECTOR}." in result


@pytest.mark.asyncio
async def test_hover_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during hover."""
    mock_element = AsyncMock()
    mock_element.hover = AsyncMock(
        side_effect=PlaywrightError("Generic hover error"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert f"Playwright error hovering over {SELECTOR}: " \
           "Generic hover error" in result


@pytest.mark.asyncio
async def test_hover_element_generic_exception(tool_manager_with_page):
    """Test generic Exception during hover."""
    mock_element = AsyncMock()
    mock_element.hover = AsyncMock(
        side_effect=Exception("Generic hover exception"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.hover_element(SELECTOR)
    assert f"Error hovering over {SELECTOR}: Generic hover exception" in result


# Tests for select_option
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "option_param, expected_call_arg",
    [
        ({"value": "val1"}, {"value": "val1"}),
        ({"label": "Label 1"}, {"label": "Label 1"}),
        ({"index": 0}, {"index": 0}),
    ],
)
async def test_select_option_success(
        tool_manager_with_page, option_param, expected_call_arg):
    """Test successful option selection by value, label, and index."""
    mock_element = AsyncMock()
    mock_element.select_option = AsyncMock(return_value=["selected_value"])
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)

    key, value = list(option_param.items())[0]
    kwargs = {key: value}
    result = await tool_manager_with_page.select_option(SELECTOR, **kwargs)

    mock_element.select_option.assert_called_once_with(**expected_call_arg)
    assert "Option specified by" in result
    assert "selected successfully for element" in result


@pytest.mark.asyncio
async def test_select_option_not_found(tool_manager_with_page):
    """Test option selection when the option is not found."""
    mock_element = AsyncMock()
    mock_element.select_option = AsyncMock(return_value=[])  # No option selected
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(
        SELECTOR, value="nonexistent")
    assert "Error: Could not select option specified by " \
           "{'value': 'nonexistent'} for element" in result


@pytest.mark.asyncio
async def test_select_option_element_not_found(tool_manager_with_page):
    """Test option selection when the select element is not found."""
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(
        SELECTOR, value="val1")
    assert f"Error: Select element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_select_option_element_not_a_select(tool_manager_with_page):
    """Test option selection when element is not a select."""
    mock_element = AsyncMock()
    error_msg = "Not a select element"
    mock_element.select_option = AsyncMock(
        side_effect=PlaywrightError(error_msg))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(
        SELECTOR, value="val1")
    assert f"Playwright error selecting option for {SELECTOR}: {error_msg}" \
           in result


@pytest.mark.asyncio
async def test_select_option_no_option_specifier(tool_manager_with_page):
    """Test option selection with no specifier."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(SELECTOR)
    assert "Error: No option specifier provided. " \
           "Use value, label, or index." in result


@pytest.mark.asyncio
async def test_select_option_multiple_option_specifiers(
        tool_manager_with_page):
    """Test option selection with multiple specifiers."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(
        SELECTOR, value="val1", label="Label1")
    assert "Error: Multiple option specifiers provided. " \
           "Use only one of value, label, or index." in result


@pytest.mark.asyncio
async def test_select_option_page_not_initialized(tool_manager_no_page):
    """Test option selection when page is not initialized."""
    result = await tool_manager_no_page.select_option(SELECTOR, value="val1")
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_select_option_page_closed(tool_manager_with_page):
    """Test option selection when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.select_option(SELECTOR, value="val1")
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_select_option_timeout_error(tool_manager_with_page):
    """Test timeout error during option selection."""
    mock_element = AsyncMock()
    mock_element.select_option = AsyncMock(
        side_effect=PlaywrightTimeoutError("Timeout selecting"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(
        SELECTOR, value="val1")
    assert f"Timeout selecting option for {SELECTOR}." in result


@pytest.mark.asyncio
async def test_select_option_playwright_error_generic(tool_manager_with_page):
    """Test generic Playwright error during option selection."""
    mock_element = AsyncMock()
    mock_element.select_option = AsyncMock(
        side_effect=PlaywrightError("Generic select error"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(
        SELECTOR, value="val1")
    assert f"Playwright error selecting option for {SELECTOR}: " \
           "Generic select error" in result


@pytest.mark.asyncio
async def test_select_option_generic_exception(tool_manager_with_page):
    """Test generic Exception during option selection."""
    mock_element = AsyncMock()
    mock_element.select_option = AsyncMock(
        side_effect=Exception("Generic select exception"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.select_option(
        SELECTOR, value="val1")
    assert f"Error selecting option for {SELECTOR}: " \
           "Generic select exception" in result


# Tests for get_element_html
@pytest.mark.asyncio
async def test_get_element_html_success_default(tool_manager_with_page):
    """Test successful HTML retrieval with default options."""
    sample_html = "<div><p>Test</p><!-- comment --><script>alert(1)</script></div>"
    mock_element = AsyncMock()
    mock_element.evaluate = AsyncMock(return_value=sample_html)
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert result == sample_html
    mock_element.evaluate.assert_called_once_with("el => el.outerHTML")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "remove_scripts, remove_comments, remove_styles, input_html, expected_html",
    [
        (True, False, False, "<div><script>s</script>Text</div>", "<div>Text</div>"),
        (False, True, False, "<div><!--c-->Text</div>", "<div>Text</div>"),
        (False, False, True, "<div><style>st</style>Text</div>", "<div>Text</div>"),
        (True, True, False, "<div><script>s</script><!--c-->Text</div>", "<div>Text</div>"),
        (True, False, True, "<div><script>s</script><style>st</style>Text</div>", "<div>Text</div>"),
        (False, True, True, "<div><!--c--><style>st</style>Text</div>", "<div>Text</div>"),
        (True, True, True, "<div><script>s</script><!--c--><style>st</style>Text</div>", "<div>Text</div>"),
    ]
)
async def test_get_element_html_success_removal_options(
    tool_manager_with_page, remove_scripts, remove_comments, remove_styles,
    input_html, expected_html
):
    """Test HTML retrieval with removal options."""
    mock_element = AsyncMock()
    mock_element.evaluate = AsyncMock(return_value=input_html)
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)

    result = await tool_manager_with_page.get_element_html(
        SELECTOR,
        remove_scripts=remove_scripts,
        remove_comments=remove_comments,
        remove_styles=remove_styles
    )
    # Basic check, more robust would use BeautifulSoup
    assert expected_html in result


@pytest.mark.asyncio
async def test_get_element_html_character_limit(tool_manager_with_page):
    """Test HTML retrieval with character limit."""
    long_html = "<a>" + "b" * 2000 + "</a>"
    expected_html_start = "<a>" + "b" * (1000 - 3 - len("<a>"))
    mock_element = AsyncMock()
    mock_element.evaluate = AsyncMock(return_value=long_html)
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_html(
        SELECTOR, max_html_length=1000)
    assert result.startswith(expected_html_start)
    assert result.endswith("...")
    assert len(result) == 1000


@pytest.mark.asyncio
async def test_get_element_html_element_not_found(tool_manager_with_page):
    """Test HTML retrieval when element is not found."""
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_html_page_not_initialized(tool_manager_no_page):
    """Test HTML retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_element_html(SELECTOR)
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_element_html_page_closed(tool_manager_with_page):
    """Test HTML retrieval when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_element_html_playwright_error(tool_manager_with_page):
    """Test Playwright error during HTML retrieval."""
    mock_element = AsyncMock()
    mock_element.evaluate = AsyncMock(
        side_effect=PlaywrightError("Evaluate error"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert f"Playwright error getting HTML for {SELECTOR}: Evaluate error" \
           in result


@pytest.mark.asyncio
async def test_get_element_html_generic_exception(tool_manager_with_page):
    """Test generic Exception during HTML retrieval."""
    mock_element = AsyncMock()
    mock_element.evaluate = AsyncMock(
        side_effect=Exception("Generic evaluate error"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_html(SELECTOR)
    assert f"Error getting HTML for {SELECTOR}: Generic evaluate error" \
           in result


# Tests for get_element_bounding_box
@pytest.mark.asyncio
async def test_get_element_bounding_box_success(tool_manager_with_page):
    """Test successful bounding box retrieval."""
    bbox = {'x': 1, 'y': 2, 'width': 10, 'height': 20}
    mock_element = AsyncMock()
    mock_element.bounding_box = AsyncMock(return_value=bbox)
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert result == bbox


@pytest.mark.asyncio
async def test_get_element_bounding_box_element_not_found(
        tool_manager_with_page):
    """Test bounding box retrieval when element is not found."""
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_not_visible(tool_manager_with_page):
    """Test bounding box retrieval when element is not visible."""
    mock_element = AsyncMock()
    mock_element.bounding_box = AsyncMock(return_value=None) # Not visible
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert f"Error: Element {SELECTOR} found, but it is not visible " \
           "or has no dimensions." in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_page_not_initialized(
        tool_manager_no_page):
    """Test bounding box retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_element_bounding_box(SELECTOR)
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_page_closed(tool_manager_with_page):
    """Test bounding box retrieval when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_playwright_error(
        tool_manager_with_page):
    """Test Playwright error during bounding box retrieval."""
    mock_element = AsyncMock()
    mock_element.bounding_box = AsyncMock(
        side_effect=PlaywrightError("Bbox error"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert f"Playwright error getting bounding box for {SELECTOR}: " \
           "Bbox error" in result


@pytest.mark.asyncio
async def test_get_element_bounding_box_generic_exception(
        tool_manager_with_page):
    """Test generic Exception during bounding box retrieval."""
    mock_element = AsyncMock()
    mock_element.bounding_box = AsyncMock(
        side_effect=Exception("Generic bbox error"))
    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_element_bounding_box(SELECTOR)
    assert f"Error getting bounding box for {SELECTOR}: " \
           "Generic bbox error" in result
