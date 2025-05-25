"""Tests for page manipulation tools in ToolManager."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, ANY

# For simulating Playwright errors and Page type
from playwright.async_api import Error as PlaywrightError, Page
# For navigation timeout
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from mcp_server.tool_manager import ToolManager  # Import ToolManager


@pytest.fixture
def tool_manager_with_page():
    """Provides a ToolManager instance with a mocked page."""
    tm = ToolManager()
    tm.page = AsyncMock(spec=Page)  # Mock the page attribute
    return tm


@pytest.fixture
def tool_manager_no_page():
    """Provides a ToolManager instance where page is initially None."""
    tm = ToolManager()
    return tm


# Tests for goto_page
@pytest.mark.asyncio
async def test_goto_page_success(tool_manager_with_page):
    """Test successful page navigation."""
    url = "https://example.com"
    result = await tool_manager_with_page.goto_page(url)
    tool_manager_with_page.page.goto.assert_called_once_with(url, timeout=ANY)
    assert f"Navigation to {url} successful." in result


@pytest.mark.asyncio
async def test_goto_page_no_page_initialized(tool_manager_no_page):
    """Test navigation when page is not initialized."""
    result = await tool_manager_no_page.goto_page("https://example.com")
    assert "Error: Page not initialized. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_goto_page_playwright_navigation_error(tool_manager_with_page):
    """Test Playwright navigation error during goto_page."""
    url = "https://example.com"
    tool_manager_with_page.page.goto.side_effect = \
        PlaywrightError("Navigation failed")
    result = await tool_manager_with_page.goto_page(url)
    assert f"Playwright nav error to {url}: Navigation failed" in result


@pytest.mark.asyncio
async def test_goto_page_playwright_timeout_error(tool_manager_with_page):
    """Test Playwright timeout error during goto_page."""
    url = "https://example.com"
    tool_manager_with_page.page.goto.side_effect = \
        PlaywrightTimeoutError("Timeout during navigation")
    result = await tool_manager_with_page.goto_page(url)
    assert f"Playwright nav error to {url}: Timeout during navigation" in result


@pytest.mark.asyncio
async def test_goto_page_general_exception(tool_manager_with_page):
    """Test general exception during goto_page."""
    url = "https://example.com"
    tool_manager_with_page.page.goto.side_effect = \
        Exception("Unexpected error")
    result = await tool_manager_with_page.goto_page(url)
    assert f"Error navigating to {url}: Unexpected error" in result


# Tests for capture_screenshot
@pytest.mark.asyncio
async def test_capture_screenshot_success(tool_manager_with_page):
    """Test successful screenshot capture."""
    # path = "/screenshots/test.png" # Path is no longer an argument
    tool_manager_with_page.page.screenshot.return_value = b"screenshot_bytes"
    result = await tool_manager_with_page.capture_screenshot()
    tool_manager_with_page.page.screenshot.assert_called_once_with()
    # assert f"Screenshot saved to {path}." in result # Path is no longer part of the success message
    assert isinstance(result, str) # Should be base64 string
    assert len(result) > 0


@pytest.mark.asyncio
async def test_capture_screenshot_no_page_initialized(tool_manager_no_page):
    """Test screenshot capture when page is not initialized."""
    result = await tool_manager_no_page.capture_screenshot() # Path is no longer an argument
    assert "Error: Page not initialized. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_capture_screenshot_playwright_error(tool_manager_with_page):
    """Test Playwright error during screenshot capture."""
    # path = "/screenshots/test.png" # Path is no longer an argument
    tool_manager_with_page.page.screenshot.side_effect = \
        PlaywrightError("Screenshot failed")
    result = await tool_manager_with_page.capture_screenshot()
    assert "Playwright error capturing screenshot: Screenshot failed" in result


@pytest.mark.asyncio
async def test_capture_screenshot_general_exception(tool_manager_with_page):
    """Test general exception during screenshot capture."""
    # path = "/screenshots/test.png" # Path is no longer an argument
    tool_manager_with_page.page.screenshot.side_effect = Exception("Disk full")
    result = await tool_manager_with_page.capture_screenshot()
    assert "Error capturing screenshot: Disk full" in result


# Tests for close_page
@pytest.mark.asyncio
async def test_close_page_success(tool_manager_with_page):
    """Test successful page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = False
    result = await tool_manager_with_page.close_page()
    mock_page_instance.close.assert_called_once()
    assert tool_manager_with_page.page is None
    assert "Page closed successfully." in result


@pytest.mark.asyncio
async def test_close_page_already_none(tool_manager_no_page):
    """Test closing page when it's already None."""
    result = await tool_manager_no_page.close_page()
    assert "No active page to close." in result
    assert tool_manager_no_page.page is None


@pytest.mark.asyncio
async def test_close_page_already_closed_on_playwright_side(
        tool_manager_with_page):
    """Test closing page when Playwright already considers it closed."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = True
    result = await tool_manager_with_page.close_page()
    mock_page_instance.close.assert_not_called()
    assert tool_manager_with_page.page is None
    assert "Page closed successfully." in result


@pytest.mark.asyncio
async def test_close_page_playwright_error_on_close(tool_manager_with_page):
    """Test Playwright error during page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = False
    mock_page_instance.close.side_effect = \
        PlaywrightError("Failed to close page via Playwright")
    result = await tool_manager_with_page.close_page()
    assert "Playwright error closing page: " \
           "Failed to close page via Playwright" in result
    assert tool_manager_with_page.page is None


@pytest.mark.asyncio
async def test_close_page_general_exception_on_close(tool_manager_with_page):
    """Test general exception during page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed.return_value = False
    mock_page_instance.close.side_effect = \
        Exception("Unexpected error during close")
    result = await tool_manager_with_page.close_page()
    assert "Error closing page: Unexpected error during close" in result
    assert tool_manager_with_page.page is None


# Tests for capture_area_snapshot
@pytest.mark.asyncio
async def test_capture_area_snapshot_full_page_success(tool_manager_with_page):
    """Test successful full page snapshot."""
    tool_manager_with_page.page.screenshot.return_value = b"full_page_bytes"
    result = await tool_manager_with_page.capture_area_snapshot()
    tool_manager_with_page.page.screenshot.assert_called_once_with(
        full_page=True
    )
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_capture_area_snapshot_element_success(tool_manager_with_page):
    """Test successful element snapshot."""
    selector = "#my-element"
    mock_element = AsyncMock()
    mock_element.screenshot.return_value = b"element_bytes"
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.capture_area_snapshot(selector)

    tool_manager_with_page.page.query_selector.assert_called_once_with(selector)
    mock_element.scroll_into_view_if_needed.assert_awaited_once()
    mock_element.screenshot.assert_called_once_with()
    assert isinstance(result, str)
    assert "element_bytes" in result # Check if the base64 encoded string contains the original bytes representation
    assert len(result) > 10 # Check if it's a reasonable length for base64 encoded string


@pytest.mark.asyncio
async def test_capture_area_snapshot_element_not_found(tool_manager_with_page):
    """Test snapshot when element is not found."""
    selector = "#not-found"
    tool_manager_with_page.page.query_selector.return_value = None
    result = await tool_manager_with_page.capture_area_snapshot(selector)
    assert f"Error: Element not found for selector: {selector}" in result
    tool_manager_with_page.page.screenshot.assert_not_called()


@pytest.mark.asyncio
async def test_capture_area_snapshot_no_page(tool_manager_no_page):
    """Test snapshot when page is not initialized."""
    result = await tool_manager_no_page.capture_area_snapshot()
    assert "Error: Page not initialized. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_page_closed(tool_manager_with_page):
    """Test snapshot when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.capture_area_snapshot()
    assert "Error: Page is closed." in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_playwright_error_full_page(
        tool_manager_with_page):
    """Test Playwright error during full page snapshot."""
    tool_manager_with_page.page.screenshot.side_effect = \
        PlaywrightError("Full page snapshot failed")
    result = await tool_manager_with_page.capture_area_snapshot()
    assert "Playwright error capturing snapshot: " \
           "Full page snapshot failed" in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_playwright_error_element(
        tool_manager_with_page):
    """Test Playwright error during element snapshot."""
    selector = "#my-element"
    mock_element = AsyncMock()
    mock_element.screenshot.side_effect = \
        PlaywrightError("Element snapshot failed")
    tool_manager_with_page.page.query_selector.return_value = mock_element

    result = await tool_manager_with_page.capture_area_snapshot(selector)
    assert "Playwright error capturing snapshot for " \
           f"{selector}: Element snapshot failed" in result


# Tests for get_current_url
@pytest.mark.asyncio
async def test_get_current_url_success(tool_manager_with_page):
    """Test successful retrieval of the current URL."""
    expected_url = "https://example.com/current-page"
    tool_manager_with_page.page.url = expected_url
    result = await tool_manager_with_page.get_current_url()
    assert result == expected_url


@pytest.mark.asyncio
async def test_get_current_url_no_page(tool_manager_no_page):
    """Test URL retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_current_url()
    assert "Error: Page not initialized. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_get_current_url_page_closed(tool_manager_with_page):
    """Test URL retrieval when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.get_current_url()
    assert "Error: Page is closed." in result


@pytest.mark.asyncio
async def test_get_current_url_playwright_error(tool_manager_with_page):
    """Test Playwright error (e.g., if page.url was a method that could fail)."""
    # In Playwright, page.url is a property, so it doesn't typically raise
    # an error on its own unless the page object itself is unusable.
    # This test simulates a scenario where accessing page properties might fail.
    del tool_manager_with_page.page.url # Make it seem like property is missing
    result = await tool_manager_with_page.get_current_url()
    assert "Error getting current URL: 'AsyncMock' object has no attribute 'url'" in result


# Tests for get_page_title
@pytest.mark.asyncio
async def test_get_page_title_success(tool_manager_with_page):
    """Test successful retrieval of the page title."""
    expected_title = "My Awesome Page"
    tool_manager_with_page.page.title.return_value = expected_title # title() is an async method
    result = await tool_manager_with_page.get_page_title()
    tool_manager_with_page.page.title.assert_awaited_once()
    assert result == expected_title


@pytest.mark.asyncio
async def test_get_page_title_no_page(tool_manager_no_page):
    """Test title retrieval when page is not initialized."""
    result = await tool_manager_no_page.get_page_title()
    assert "Error: Page not initialized. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_get_page_title_page_closed(tool_manager_with_page):
    """Test title retrieval when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.get_page_title()
    assert "Error: Page is closed." in result
    tool_manager_with_page.page.title.assert_not_called()


@pytest.mark.asyncio
async def test_get_page_title_playwright_error(tool_manager_with_page):
    """Test Playwright error during title retrieval."""
    tool_manager_with_page.page.title.side_effect = \
        PlaywrightError("Failed to get title")
    result = await tool_manager_with_page.get_page_title()
    assert "Playwright error getting page title: Failed to get title" in result


# Tests for wait_for_navigation
@pytest.mark.asyncio
async def test_wait_for_navigation_success_specific_url(tool_manager_with_page):
    """Test successful wait for navigation to a specific URL."""
    url_to_wait_for = "https://example.com/nextpage"
    mock_response = AsyncMock() # Simulate a response object
    mock_response.status = 200
    mock_response.url = url_to_wait_for
    tool_manager_with_page.page.wait_for_navigation.return_value = mock_response

    result = await tool_manager_with_page.wait_for_navigation(
        url=url_to_wait_for, timeout_ms=5000)

    tool_manager_with_page.page.wait_for_navigation.assert_awaited_once_with(
        url=url_to_wait_for, timeout=5000.0, wait_until=None)
    assert f"Navigation to {url_to_wait_for} completed. Status: 200." in result


@pytest.mark.asyncio
async def test_wait_for_navigation_success_wait_until(tool_manager_with_page):
    """Test successful wait with a wait_until condition."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.url = "https://example.com/loaded"
    tool_manager_with_page.page.wait_for_navigation.return_value = mock_response

    result = await tool_manager_with_page.wait_for_navigation(
        wait_until='networkidle', timeout_ms=5000)

    tool_manager_with_page.page.wait_for_navigation.assert_awaited_once_with(
        url=None, timeout=5000.0, wait_until='networkidle')
    assert "Navigation (event: networkidle) completed. Status: 200. URL: https://example.com/loaded" in result


@pytest.mark.asyncio
async def test_wait_for_navigation_timeout_conversion(tool_manager_with_page):
    """Test timeout is correctly converted to milliseconds for Playwright."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.url = "https://example.com/timeout-test"
    tool_manager_with_page.page.wait_for_navigation.return_value = mock_response

    await tool_manager_with_page.wait_for_navigation(timeout_ms=2500)
    args, kwargs = tool_manager_with_page.page.wait_for_navigation.call_args
    assert kwargs['timeout'] == 2500.0 # Playwright expects float milliseconds


@pytest.mark.asyncio
async def test_wait_for_navigation_timeout_error(tool_manager_with_page):
    """Test timeout error during wait_for_navigation."""
    tool_manager_with_page.page.wait_for_navigation.side_effect = \
        PlaywrightTimeoutError("Navigation timed out")
    result = await tool_manager_with_page.wait_for_navigation(timeout_ms=100)
    assert "Timeout waiting for navigation (100.0ms)." in result


@pytest.mark.asyncio
async def test_wait_for_navigation_no_page(tool_manager_no_page):
    """Test wait_for_navigation when page is not initialized."""
    result = await tool_manager_no_page.wait_for_navigation()
    assert "Error: Page not initialized. Call 'new_page' first." in result


@pytest.mark.asyncio
async def test_wait_for_navigation_page_closed(tool_manager_with_page):
    """Test wait_for_navigation when page is closed."""
    tool_manager_with_page.page.is_closed.return_value = True
    result = await tool_manager_with_page.wait_for_navigation()
    assert "Error: Page is closed." in result
    tool_manager_with_page.page.wait_for_navigation.assert_not_called()


@pytest.mark.asyncio
async def test_wait_for_navigation_playwright_error(tool_manager_with_page):
    """Test general Playwright error during wait_for_navigation."""
    tool_manager_with_page.page.wait_for_navigation.side_effect = \
        PlaywrightError("Generic Playwright wait error")
    result = await tool_manager_with_page.wait_for_navigation()
    assert "Playwright error during navigation wait: " \
           "Generic Playwright wait error" in result


@pytest.mark.asyncio
async def test_wait_for_navigation_returns_mock_response(tool_manager_with_page):
    """Test that the method handles a mock response object correctly."""
    mock_response = AsyncMock()
    mock_response.status = 201 # Non-200 status
    mock_response.url = "https://example.com/created"
    tool_manager_with_page.page.wait_for_navigation.return_value = mock_response

    result = await tool_manager_with_page.wait_for_navigation(
        url="https://example.com/created")
    assert "Navigation to https://example.com/created completed. " \
           "Status: 201." in result


@pytest.mark.asyncio
async def test_wait_for_navigation_returns_none_response(tool_manager_with_page):
    """Test behavior if wait_for_navigation returns None (e.g. about:blank navs)."""
    # Playwright's wait_for_navigation typically returns a Response object or raises an error.
    # A None response is common for navigations to "about:blank" or similar.
    tool_manager_with_page.page.wait_for_navigation.return_value = None
    url_to_wait_for = "about:blank"
    result = await tool_manager_with_page.wait_for_navigation(url=url_to_wait_for)
    assert f"Navigation to {url_to_wait_for} completed, but no response object was received (e.g., 'about:blank')." in result

    # Test with no specific URL (general navigation event)
    tool_manager_with_page.page.wait_for_navigation.return_value = None
    result = await tool_manager_with_page.wait_for_navigation(wait_until="load")
    assert "Navigation (event: load) completed, but no response object was received (e.g., 'about:blank')." in result
