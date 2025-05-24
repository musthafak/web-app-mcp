"""Tests for page manipulation tools in ToolManager."""
import pytest
from unittest.mock import MagicMock

# For simulating Playwright errors and Page type
from playwright.sync_api import Error as PlaywrightError, Page
# For navigation timeout
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from mcp_server.tool_manager import ToolManager  # Import ToolManager


@pytest.fixture
def tool_manager_with_page():
    """Provides a ToolManager instance with a mocked page."""
    tm = ToolManager()
    tm.page = MagicMock(spec=Page)  # Mock the page attribute
    return tm


@pytest.fixture
def tool_manager_no_page():
    """Provides a ToolManager instance where page is initially None."""
    tm = ToolManager()
    return tm


# Tests for goto_page
def test_goto_page_success(tool_manager_with_page):
    """Test successful page navigation."""
    url = "https://example.com"
    result = tool_manager_with_page.goto_page(url)
    tool_manager_with_page.page.goto.assert_called_once_with(url)
    assert f"Navigation to {url} successful." in result


def test_goto_page_no_page_initialized(tool_manager_no_page):
    """Test navigation when page is not initialized."""
    result = tool_manager_no_page.goto_page("https://example.com")
    assert "Error: Page not initialized. Call 'new_page' first." in result


def test_goto_page_playwright_navigation_error(tool_manager_with_page):
    """Test Playwright navigation error during goto_page."""
    url = "https://example.com"
    tool_manager_with_page.page.goto.side_effect = \
        PlaywrightError("Navigation failed")
    result = tool_manager_with_page.goto_page(url)
    assert f"Playwright nav error to {url}: Navigation failed" in result


def test_goto_page_playwright_timeout_error(tool_manager_with_page):
    """Test Playwright timeout error during goto_page."""
    url = "https://example.com"
    tool_manager_with_page.page.goto.side_effect = \
        PlaywrightTimeoutError("Timeout during navigation")
    result = tool_manager_with_page.goto_page(url)
    assert f"Playwright nav error to {url}: Timeout during navigation" in result


def test_goto_page_general_exception(tool_manager_with_page):
    """Test general exception during goto_page."""
    url = "https://example.com"
    tool_manager_with_page.page.goto.side_effect = \
        Exception("Unexpected error")
    result = tool_manager_with_page.goto_page(url)
    assert f"Error navigating to {url}: Unexpected error" in result


# Tests for capture_screenshot
def test_capture_screenshot_success(tool_manager_with_page):
    """Test successful screenshot capture."""
    path = "/screenshots/test.png"
    result = tool_manager_with_page.capture_screenshot(path)
    tool_manager_with_page.page.screenshot.assert_called_once_with(path=path)
    assert f"Screenshot saved to {path}." in result


def test_capture_screenshot_no_page_initialized(tool_manager_no_page):
    """Test screenshot capture when page is not initialized."""
    result = tool_manager_no_page.capture_screenshot("/screenshots/test.png")
    assert "Error: Page not initialized. Call 'new_page' first." in result


def test_capture_screenshot_playwright_error(tool_manager_with_page):
    """Test Playwright error during screenshot capture."""
    path = "/screenshots/test.png"
    tool_manager_with_page.page.screenshot.side_effect = \
        PlaywrightError("Screenshot failed")
    result = tool_manager_with_page.capture_screenshot(path)
    assert "Playwright error capturing screenshot to " \
           f"{path}: Screenshot failed" in result


def test_capture_screenshot_general_exception(tool_manager_with_page):
    """Test general exception during screenshot capture."""
    path = "/screenshots/test.png"
    tool_manager_with_page.page.screenshot.side_effect = Exception("Disk full")
    result = tool_manager_with_page.capture_screenshot(path)
    assert "Error capturing screenshot to " \
           f"{path}: Disk full. Ensure path is valid/writable." in result


# Tests for close_page
def test_close_page_success(tool_manager_with_page):
    """Test successful page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = False
    result = tool_manager_with_page.close_page()
    mock_page_instance.close.assert_called_once()
    assert tool_manager_with_page.page is None
    assert "Page closed successfully." in result


def test_close_page_already_none(tool_manager_no_page):
    """Test closing page when it's already None."""
    result = tool_manager_no_page.close_page()
    assert "No active page to close." in result
    assert tool_manager_no_page.page is None


def test_close_page_already_closed_on_playwright_side(
        tool_manager_with_page):
    """Test closing page when Playwright already considers it closed."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = True
    result = tool_manager_with_page.close_page()
    mock_page_instance.close.assert_not_called()
    assert tool_manager_with_page.page is None
    assert "Page closed successfully." in result


def test_close_page_playwright_error_on_close(tool_manager_with_page):
    """Test Playwright error during page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = False
    mock_page_instance.close.side_effect = \
        PlaywrightError("Failed to close page via Playwright")
    result = tool_manager_with_page.close_page()
    assert "Playwright error closing page: " \
           "Failed to close page via Playwright" in result
    assert tool_manager_with_page.page is None


def test_close_page_general_exception_on_close(tool_manager_with_page):
    """Test general exception during page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = False
    mock_page_instance.close.side_effect = \
        Exception("Unexpected error during close")
    result = tool_manager_with_page.close_page()
    assert "Error closing page: Unexpected error during close" in result
    assert tool_manager_with_page.page is None
