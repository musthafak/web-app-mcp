"""Tests for page manipulation tools in ToolManager."""
import pytest
from unittest.mock import AsyncMock, MagicMock

# For simulating Playwright errors and Page type
from playwright.async_api import Error as PlaywrightError, Page
# For navigation timeout
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from mcp_server.tool_manager import ToolManager  # Import ToolManager


@pytest.fixture
async def tool_manager_with_page():
    """Provides a ToolManager instance with a mocked page."""
    tm = ToolManager()
    tm.page = AsyncMock(spec=Page)  # Mock the page attribute
    return tm


@pytest.fixture
async def tool_manager_no_page():
    """Provides a ToolManager instance where page is initially None."""
    tm = ToolManager()
    return tm


# Tests for goto_page
@pytest.mark.asyncio
async def test_goto_page_success(tool_manager_with_page):
    """Test successful page navigation."""
    url = "https://example.com"
    result = await tool_manager_with_page.goto_page(url)
    tool_manager_with_page.page.goto.assert_called_once_with(url)
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
    fake_image_bytes = b"fakedata"
    expected_base64_string = "ZmFrZWRhdGE="  # base64.b64encode(b"fakedata").decode()
    tool_manager_with_page.page.screenshot = AsyncMock(
        return_value=fake_image_bytes)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)

    result = await tool_manager_with_page.capture_screenshot()

    tool_manager_with_page.page.screenshot.assert_called_once_with()
    assert result == expected_base64_string
@pytest.mark.asyncio
async def test_capture_screenshot_page_not_initialized(tool_manager_no_page):
    """Test screenshot capture when page is not initialized."""
    result = await tool_manager_no_page.capture_screenshot()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_capture_screenshot_page_closed(tool_manager_with_page):
    """Test screenshot capture when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.capture_screenshot()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_capture_screenshot_playwright_error(tool_manager_with_page):
    """Test Playwright error during screenshot capture."""
    tool_manager_with_page.page.screenshot.side_effect = \
        PlaywrightError("Screenshot failed")
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.capture_screenshot()
    assert "Playwright error capturing screenshot: Screenshot failed" in result


@pytest.mark.asyncio
async def test_capture_screenshot_general_exception(tool_manager_with_page):
    """Test general exception during screenshot capture."""
    tool_manager_with_page.page.screenshot.side_effect = Exception("Generic screenshot error")
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.capture_screenshot()
    assert "Error capturing screenshot: Generic screenshot error" in result


# Tests for close_page
@pytest.mark.asyncio
async def test_close_page_success(tool_manager_with_page):
    """Test successful page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed = MagicMock(return_value=False)
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
    mock_page_instance.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.close_page()
    mock_page_instance.close.assert_not_called()
    assert tool_manager_with_page.page is None
    assert "Page closed successfully." in result


@pytest.mark.asyncio
async def test_close_page_playwright_error_on_close(tool_manager_with_page):
    """Test Playwright error during page closure."""
    mock_page_instance = tool_manager_with_page.page
    mock_page_instance.is_closed = MagicMock(return_value=False)
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
    mock_page_instance.is_closed = MagicMock(return_value=False)
    mock_page_instance.close.side_effect = \
        Exception("Unexpected error during close")
    result = await tool_manager_with_page.close_page()
    assert "Error closing page: Unexpected error during close" in result
    assert tool_manager_with_page.page is None


# Tests for get_current_url
@pytest.mark.asyncio
async def test_get_current_url_success(tool_manager_with_page):
    """Test successful retrieval of the current URL."""
    expected_url = "https://example.com/current"
    # Mock page.url as a property
    type(tool_manager_with_page.page).url = PropertyMock(
        return_value=expected_url)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)

    result = await tool_manager_with_page.get_current_url()
    assert result == expected_url


@pytest.mark.asyncio
async def test_get_current_url_page_not_initialized(tool_manager_no_page):
    """Test get_current_url when page is not initialized."""
    result = await tool_manager_no_page.get_current_url()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_current_url_page_closed(tool_manager_with_page):
    """Test get_current_url when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.get_current_url()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_current_url_playwright_error(tool_manager_with_page):
    """Test Playwright error during get_current_url."""
    type(tool_manager_with_page.page).url = PropertyMock(
        side_effect=PlaywrightError("URL access failed"))
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_current_url()
    assert "Playwright error getting current URL: URL access failed" in result


@pytest.mark.asyncio
async def test_get_current_url_generic_exception(tool_manager_with_page):
    """Test generic Exception during get_current_url."""
    type(tool_manager_with_page.page).url = PropertyMock(
        side_effect=Exception("Generic URL access failed"))
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_current_url()
    assert "Error getting current URL: Generic URL access failed" in result


# Tests for get_page_title
@pytest.mark.asyncio
async def test_get_page_title_success(tool_manager_with_page):
    """Test successful retrieval of the page title."""
    expected_title = "Test Page Title"
    tool_manager_with_page.page.title = AsyncMock(return_value=expected_title)
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)

    result = await tool_manager_with_page.get_page_title()
    assert result == expected_title
    tool_manager_with_page.page.title.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_title_page_not_initialized(tool_manager_no_page):
    """Test get_page_title when page is not initialized."""
    result = await tool_manager_no_page.get_page_title()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_page_title_page_closed(tool_manager_with_page):
    """Test get_page_title when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.get_page_title()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_get_page_title_playwright_error(tool_manager_with_page):
    """Test Playwright error during get_page_title."""
    tool_manager_with_page.page.title = AsyncMock(
        side_effect=PlaywrightError("Title access failed"))
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_page_title()
    assert "Playwright error getting page title: Title access failed" in result


@pytest.mark.asyncio
async def test_get_page_title_generic_exception(tool_manager_with_page):
    """Test generic Exception during get_page_title."""
    tool_manager_with_page.page.title = AsyncMock(
        side_effect=Exception("Generic Title access failed"))
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    result = await tool_manager_with_page.get_page_title()
    assert "Error getting page title: Generic Title access failed" in result


# Tests for wait_for_navigation
@pytest.mark.asyncio
async def test_wait_for_navigation_success_basic(tool_manager_with_page):
    """Test successful basic wait for navigation."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    mock_response = AsyncMock()
    tool_manager_with_page.page.wait_for_navigation = AsyncMock(
        return_value=mock_response)

    result = await tool_manager_with_page.wait_for_navigation()
    assert "Navigation completed." in result
    tool_manager_with_page.page.wait_for_navigation.assert_called_once_with(
        url=None, wait_until=None, timeout=None
    )


@pytest.mark.asyncio
async def test_wait_for_navigation_success_with_options(
        tool_manager_with_page):
    """Test successful wait for navigation with options."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    mock_response = AsyncMock()
    tool_manager_with_page.page.wait_for_navigation = AsyncMock(
        return_value=mock_response)
    url_pattern = "**/checkout"
    wait_until_event = "load"
    timeout_sec = 10
    timeout_ms = timeout_sec * 1000

    result = await tool_manager_with_page.wait_for_navigation(
        url=url_pattern, wait_until=wait_until_event, timeout=timeout_sec
    )
    assert "Navigation completed." in result
    tool_manager_with_page.page.wait_for_navigation.assert_called_once_with(
        url=url_pattern, wait_until=wait_until_event, timeout=timeout_ms
    )


@pytest.mark.asyncio
async def test_wait_for_navigation_timeout_error(tool_manager_with_page):
    """Test timeout error during wait_for_navigation."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    tool_manager_with_page.page.wait_for_navigation = AsyncMock(
        side_effect=PlaywrightTimeoutError("Navigation timeout"))

    result = await tool_manager_with_page.wait_for_navigation(timeout=5)
    assert "Timeout waiting for navigation (5s)." in result


@pytest.mark.asyncio
async def test_wait_for_navigation_page_not_initialized(
        tool_manager_no_page):
    """Test wait_for_navigation when page is not initialized."""
    result = await tool_manager_no_page.wait_for_navigation()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_wait_for_navigation_page_closed(tool_manager_with_page):
    """Test wait_for_navigation when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.wait_for_navigation()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_wait_for_navigation_playwright_error(tool_manager_with_page):
    """Test Playwright error during wait_for_navigation."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    tool_manager_with_page.page.wait_for_navigation = AsyncMock(
        side_effect=PlaywrightError("Generic navigation error"))

    result = await tool_manager_with_page.wait_for_navigation()
    assert "Playwright error waiting for navigation: " \
           "Generic navigation error" in result
@pytest.mark.asyncio
async def test_wait_for_navigation_generic_exception(tool_manager_with_page):
    """Test generic Exception during wait_for_navigation."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    tool_manager_with_page.page.wait_for_navigation = AsyncMock(
        side_effect=Exception("Generic wait error"))

    result = await tool_manager_with_page.wait_for_navigation()
    assert "Error waiting for navigation: Generic wait error" in result


# Tests for capture_area_snapshot
@pytest.mark.asyncio
async def test_capture_area_snapshot_success_whole_page(
        tool_manager_with_page):
    """Test successful AOM snapshot of the whole page."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    mock_snapshot_data = {"role": "document", "name": "Page Title"}
    # Ensure accessibility is an AsyncMock, and its snapshot method is also one
    tool_manager_with_page.page.accessibility = AsyncMock()
    tool_manager_with_page.page.accessibility.snapshot = AsyncMock(
        return_value=mock_snapshot_data
    )

    result = await tool_manager_with_page.capture_area_snapshot()
    assert result == mock_snapshot_data
    tool_manager_with_page.page.accessibility.snapshot.assert_called_once_with(
        root=None
    )


@pytest.mark.asyncio
async def test_capture_area_snapshot_success_with_selector(
        tool_manager_with_page):
    """Test successful AOM snapshot with a selector."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    selector = "#my-element"
    mock_element_handle = AsyncMock()
    mock_snapshot_data = {"role": "button", "name": "Submit"}

    tool_manager_with_page.page.query_selector = AsyncMock(
        return_value=mock_element_handle
    )
    mock_element_handle.scroll_into_view_if_needed = AsyncMock()
    tool_manager_with_page.page.accessibility = AsyncMock()
    tool_manager_with_page.page.accessibility.snapshot = AsyncMock(
        return_value=mock_snapshot_data
    )

    result = await tool_manager_with_page.capture_area_snapshot(selector)
    assert result == mock_snapshot_data
    tool_manager_with_page.page.query_selector.assert_called_once_with(
        selector)
    mock_element_handle.scroll_into_view_if_needed.assert_called_once()
    tool_manager_with_page.page.accessibility.snapshot.assert_called_once_with(
        root=mock_element_handle
    )


@pytest.mark.asyncio
async def test_capture_area_snapshot_element_not_found(
        tool_manager_with_page):
    """Test AOM snapshot when element is not found."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    selector = "#nonexistent"
    tool_manager_with_page.page.query_selector = AsyncMock(return_value=None)

    result = await tool_manager_with_page.capture_area_snapshot(selector)
    assert f"Error: Element not found for selector: {selector}" in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_page_not_initialized(
        tool_manager_no_page):
    """Test AOM snapshot when page is not initialized."""
    result = await tool_manager_no_page.capture_area_snapshot()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_page_closed(tool_manager_with_page):
    """Test AOM snapshot when page is closed."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=True)
    result = await tool_manager_with_page.capture_area_snapshot()
    assert "Error: Page not initialized or has been closed" in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_playwright_error(tool_manager_with_page):
    """Test Playwright error during AOM snapshot."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    tool_manager_with_page.page.accessibility = AsyncMock()
    tool_manager_with_page.page.accessibility.snapshot = AsyncMock(
        side_effect=PlaywrightError("Snapshot failed")
    )

    result = await tool_manager_with_page.capture_area_snapshot()
    assert "Playwright error capturing AOM snapshot: Snapshot failed" in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_selector_query_generic_exception(
        tool_manager_with_page):
    """Test generic Exception during page.query_selector in snapshot."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    selector = "#my-element"
    tool_manager_with_page.page.query_selector = AsyncMock(
        side_effect=Exception("Generic query error"))

    result = await tool_manager_with_page.capture_area_snapshot(selector)
    assert f"Error querying element for AOM snapshot: Generic query error" in result


@pytest.mark.asyncio
async def test_capture_area_snapshot_accessibility_generic_exception(
        tool_manager_with_page):
    """Test generic Exception during accessibility.snapshot."""
    tool_manager_with_page.page.is_closed = MagicMock(return_value=False)
    tool_manager_with_page.page.accessibility = AsyncMock()
    tool_manager_with_page.page.accessibility.snapshot = AsyncMock(
        side_effect=Exception("Generic snapshot error"))

    result = await tool_manager_with_page.capture_area_snapshot()
    assert "Error capturing AOM snapshot: Generic snapshot error" in result
