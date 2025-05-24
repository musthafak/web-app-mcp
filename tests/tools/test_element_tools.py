"""Tests for element interaction tools in ToolManager."""
import pytest
from unittest.mock import MagicMock

# Import Page for spec
from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    Page
)
from mcp_server.tool_manager import ToolManager


@pytest.fixture
def tool_manager_with_page():
    """Provides a ToolManager instance with a mocked page."""
    tm = ToolManager()
    tm.page = MagicMock(spec=Page)
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
def test_click_element_success(tool_manager_with_page):
    """Test successful element click."""
    result = tool_manager_with_page.click_element(SELECTOR)
    tool_manager_with_page.page.click.assert_called_once_with(SELECTOR)
    assert f"Element {SELECTOR} clicked successfully." in result


def test_click_element_no_page(tool_manager_no_page):
    """Test element click when page is not initialized."""
    result = tool_manager_no_page.click_element(SELECTOR)
    assert "Error: Page not initialized." in result


def test_click_element_timeout_error(tool_manager_with_page):
    """Test timeout error during element click."""
    tool_manager_with_page.page.click.side_effect = \
        PlaywrightTimeoutError("Timeout clicking")
    result = tool_manager_with_page.click_element(SELECTOR)
    assert f"Timeout clicking {SELECTOR}. " \
           "Element may not be visible or interactable." in result


def test_click_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element click."""
    tool_manager_with_page.page.click.side_effect = \
        PlaywrightError("Generic Playwright error")
    result = tool_manager_with_page.click_element(SELECTOR)
    assert f"PWE clicking {SELECTOR}: Generic Playwright error" in result


# Tests for fill_element
def test_fill_element_success(tool_manager_with_page):
    """Test successful element fill."""
    result = tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    tool_manager_with_page.page.fill.assert_called_once_with(
        SELECTOR, TEXT_TO_FILL)
    assert f"Text '{TEXT_TO_FILL}' filled into element " \
           f"{SELECTOR} successfully." in result


def test_fill_element_no_page(tool_manager_no_page):
    """Test element fill when page is not initialized."""
    result = tool_manager_no_page.fill_element(SELECTOR, TEXT_TO_FILL)
    assert "Error: Page not initialized." in result


def test_fill_element_timeout_error(tool_manager_with_page):
    """Test timeout error during element fill."""
    tool_manager_with_page.page.fill.side_effect = \
        PlaywrightTimeoutError("Timeout filling")
    result = tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    assert f"Timeout filling {SELECTOR}. " \
           "Element may not be visible or an input field." in result


def test_fill_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element fill."""
    tool_manager_with_page.page.fill.side_effect = \
        PlaywrightError("Generic Playwright error filling")
    result = tool_manager_with_page.fill_element(SELECTOR, TEXT_TO_FILL)
    assert "PWE filling " \
           f"{SELECTOR}: Generic Playwright error filling" in result


# Tests for capture_elements
def test_capture_elements_success(tool_manager_with_page):
    """Test successful element capture."""
    mock_element1 = MagicMock()
    mock_element1.inner_text.return_value = "Text 1"
    mock_element1.inner_html.return_value = "<p>Html 1</p>"
    mock_element1.evaluate_handle.return_value.json_value.return_value = \
        [{'name': 'class', 'value': 'btn'}]

    mock_element2 = MagicMock()
    mock_element2.inner_text.return_value = "Text 2"
    mock_element2.inner_html.return_value = "<div>Html 2</div>"
    mock_element2.evaluate_handle.return_value.json_value.return_value = \
        [{'name': 'id', 'value': 'el2'}]

    tool_manager_with_page.page.query_selector_all.return_value = \
        [mock_element1, mock_element2]
    result = tool_manager_with_page.capture_elements(SELECTOR)
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


def test_capture_elements_no_elements_found(tool_manager_with_page):
    """Test element capture when no elements are found."""
    tool_manager_with_page.page.query_selector_all.return_value = []
    result = tool_manager_with_page.capture_elements(SELECTOR)
    assert f"No elements found matching selector: {SELECTOR}" in result


def test_capture_elements_no_page(tool_manager_no_page):
    """Test element capture when page is not initialized."""
    result = tool_manager_no_page.capture_elements(SELECTOR)
    assert "Error: Page not initialized." in result


def test_capture_elements_playwright_error(tool_manager_with_page):
    """Test Playwright error during element capture."""
    tool_manager_with_page.page.query_selector_all.side_effect = \
        PlaywrightError("Query error")
    result = tool_manager_with_page.capture_elements(SELECTOR)
    assert f"PWE capturing elements for {SELECTOR}: Query error" in result


# Tests for evaluate_element
def test_evaluate_element_success(tool_manager_with_page):
    """Test successful element evaluation."""
    mock_element = MagicMock()
    mock_element.evaluate.return_value = "evaluated_value"
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.evaluate_element(SELECTOR, EXPRESSION)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.evaluate.assert_called_once_with(EXPRESSION)
    assert result == "evaluated_value"


def test_evaluate_element_no_element_found(tool_manager_with_page):
    """Test element evaluation when no element is found."""
    tool_manager_with_page.page.query_selector.return_value = None
    result = tool_manager_with_page.evaluate_element(SELECTOR, EXPRESSION)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


def test_evaluate_element_no_page(tool_manager_no_page):
    """Test element evaluation when page is not initialized."""
    result = tool_manager_no_page.evaluate_element(SELECTOR, EXPRESSION)
    assert "Error: Page not initialized." in result


def test_evaluate_element_playwright_error(tool_manager_with_page):
    """Test Playwright error during element evaluation."""
    mock_element = MagicMock()
    mock_element.evaluate.side_effect = PlaywrightError("Evaluation error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.evaluate_element(SELECTOR, EXPRESSION)
    assert f"PWE evaluating expr '{EXPRESSION}' on " \
           f"{SELECTOR}: Evaluation error" in result


def test_evaluate_element_evaluation_js_error(tool_manager_with_page):
    """Test JavaScript error during element evaluation."""
    mock_element = MagicMock()
    mock_element.evaluate.side_effect = \
        PlaywrightError("JS execution failed in evaluate")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.evaluate_element(
        SELECTOR, "invalid js expression")
    assert "PWE evaluating expr 'invalid js expression' on" in result


# Tests for get_element_attribute
def test_get_element_attribute_success(tool_manager_with_page):
    """Test successful retrieval of an element attribute."""
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "test-value"
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.get_attribute.assert_called_once_with(ATTRIBUTE_NAME)
    assert result == "test-value"


def test_get_element_attribute_not_found(tool_manager_with_page):
    """Test retrieval of a non-existent element attribute."""
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = None
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.get_element_attribute(
        SELECTOR, "nonexistent-attr")
    assert "Attribute 'nonexistent-attr' not found for element " \
           f"{SELECTOR}" in result


def test_get_element_attribute_element_not_found(tool_manager_with_page):
    """Test attribute retrieval when element is not found."""
    tool_manager_with_page.page.query_selector.return_value = None
    result = tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


def test_get_element_attribute_no_page(tool_manager_no_page):
    """Test attribute retrieval when page is not initialized."""
    result = tool_manager_no_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert "Error: Page not initialized." in result


def test_get_element_attribute_playwright_error(tool_manager_with_page):
    """Test Playwright error during attribute retrieval."""
    mock_element = MagicMock()
    mock_element.get_attribute.side_effect = \
        PlaywrightError("Get attribute error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.get_element_attribute(
        SELECTOR, ATTRIBUTE_NAME)
    assert f"PWE getting attr '{ATTRIBUTE_NAME}' for " \
           f"{SELECTOR}: Get attribute error" in result


# Tests for get_text_content
def test_get_text_content_success(tool_manager_with_page):
    """Test successful retrieval of text content."""
    mock_element = MagicMock()
    mock_element.text_content.return_value = "Expected Text"
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.get_text_content(SELECTOR)
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        SELECTOR)
    mock_element.text_content.assert_called_once()
    assert result == "Expected Text"


def test_get_text_content_element_not_found(tool_manager_with_page):
    """Test text content retrieval when element is not found."""
    tool_manager_with_page.page.query_selector.return_value = None
    result = tool_manager_with_page.get_text_content(SELECTOR)
    assert f"Error: Element not found for selector: {SELECTOR}" in result


def test_get_text_content_no_page(tool_manager_no_page):
    """Test text content retrieval when page is not initialized."""
    result = tool_manager_no_page.get_text_content(SELECTOR)
    assert "Error: Page not initialized." in result


def test_get_text_content_playwright_error(tool_manager_with_page):
    """Test Playwright error during text content retrieval."""
    mock_element = MagicMock()
    mock_element.text_content.side_effect = PlaywrightError("Get text error")
    tool_manager_with_page.page.query_selector.return_value = mock_element
    result = tool_manager_with_page.get_text_content(SELECTOR)
    assert f"PWE getting text for {SELECTOR}: Get text error" in result


# Tests for wait_for_selector
def test_wait_for_selector_success(tool_manager_with_page):
    """Test successful waiting for a selector."""
    result = tool_manager_with_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    tool_manager_with_page.page.wait_for_selector.assert_called_once_with(
        SELECTOR, timeout=float(TIMEOUT_MS))
    assert f"Element {SELECTOR} found." in result


def test_wait_for_selector_no_page(tool_manager_no_page):
    """Test waiting for selector when page is not initialized."""
    result = tool_manager_no_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    assert "Error: Page not initialized." in result


def test_wait_for_selector_timeout_error(tool_manager_with_page):
    """Test timeout error while waiting for a selector."""
    tool_manager_with_page.page.wait_for_selector.side_effect = \
        PlaywrightTimeoutError("Timeout waiting for selector")
    result = tool_manager_with_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    assert f"Timeout waiting for element {SELECTOR}." in result


def test_wait_for_selector_playwright_error(tool_manager_with_page):
    """Test Playwright error while waiting for a selector."""
    tool_manager_with_page.page.wait_for_selector.side_effect = \
        PlaywrightError("Generic Playwright wait error")
    result = tool_manager_with_page.wait_for_selector(SELECTOR, TIMEOUT_MS)
    assert "PWE waiting for " \
           f"{SELECTOR}: Generic Playwright wait error" in result
