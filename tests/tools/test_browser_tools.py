"""Tests for browser manipulation tools in ToolManager."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY

# For simulating Playwright errors
from playwright.async_api import Error as PlaywrightError
from mcp_server.tool_manager import ToolManager  # Import ToolManager


@pytest.fixture
async def tool_manager():
    """Provides a fresh ToolManager instance for each test."""
    tm = ToolManager()
    # Prevent actual Playwright calls during most tests by default
    tm.playwright = AsyncMock()
    return tm


@pytest.mark.asyncio
@pytest.mark.parametrize("headless_param", [True, False])
async def test_launch_browser_success_chromium(tool_manager, headless_param):
    """Test successful launch of Chromium with headless option."""
    tool_manager.playwright = None  # Intentionally None to test auto-start
    with patch('mcp_server.tool_manager.async_playwright') \
            as mock_async_playwright_global:
        mock_playwright_instance = AsyncMock()
        mock_async_playwright_global.return_value.start = AsyncMock(
            return_value=mock_playwright_instance)
        mock_browser_obj = AsyncMock()
        mock_playwright_instance.chromium.launch = AsyncMock(
            return_value=mock_browser_obj)
        mock_context_obj = AsyncMock()
        mock_browser_obj.new_context = AsyncMock(
            return_value=mock_context_obj)

        result = await tool_manager.launch_browser(browser_name='chromium',
                                                   headless=headless_param)

        assert "chromium browser launched successfully" in result
        mock_async_playwright_global.return_value.start.assert_called_once()
        mock_playwright_instance.chromium.launch.assert_called_once_with(
            headless=headless_param)
        assert tool_manager.browser == mock_browser_obj
        mock_browser_obj.new_context.assert_called_once()
        assert tool_manager.context == mock_context_obj


@pytest.mark.asyncio
@patch('mcp_server.tool_manager.async_playwright')
async def test_launch_browser_starts_playwright_if_none(
        mock_async_playwright_global, tool_manager):
    """Test that Playwright is started if tool_manager.playwright is None."""
    tool_manager.playwright = None  # Explicitly set to None
    mock_playwright_started_instance = AsyncMock()
    mock_async_playwright_global.return_value.start = AsyncMock(
        return_value=mock_playwright_started_instance)
    mock_browser_obj = AsyncMock()
    mock_playwright_started_instance.chromium.launch = AsyncMock(
        return_value=mock_browser_obj)
    mock_context_obj = AsyncMock()
    mock_browser_obj.new_context = AsyncMock(return_value=mock_context_obj)

    result = await tool_manager.launch_browser(browser_name='chromium',
                                               headless=True)

    mock_async_playwright_global.return_value.start.assert_called_once()
    assert tool_manager.playwright == mock_playwright_started_instance
    mock_playwright_started_instance.chromium.launch.assert_called_once_with(
        headless=True)
    assert "chromium browser launched successfully" in result
    assert tool_manager.browser is not None
    assert tool_manager.context is not None


@pytest.mark.asyncio
async def test_launch_browser_playwright_start_generic_exception(tool_manager):
    """Test generic Exception during Playwright start."""
    tool_manager.playwright = None
    with patch('mcp_server.tool_manager.async_playwright') \
            as mock_async_playwright_global:
        mock_async_playwright_global.return_value.start.side_effect = \
            Exception("Generic Start Failed")
        result = await tool_manager.launch_browser(browser_name='chromium')
        assert "Error starting Playwright: Generic Start Failed" in result
        assert tool_manager.playwright is None
        assert tool_manager.browser is None
        assert tool_manager.context is None


@pytest.mark.asyncio
async def test_launch_browser_browser_launch_generic_exception(tool_manager):
    """Test generic Exception during browser.launch()."""
    original_playwright_mock = tool_manager.playwright
    tool_manager.browser = None
    original_playwright_mock.chromium.launch.side_effect = \
        Exception("Generic Launch Failed")
    result = await tool_manager.launch_browser(browser_name='chromium')
    assert "Error launching browser chromium: Generic Launch Failed" in result
    assert tool_manager.browser is None
    assert tool_manager.context is None
    original_playwright_mock.stop.assert_called_once() # Ensure cleanup
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_launch_browser_new_context_generic_exception(tool_manager):
    """Test generic Exception during browser.new_context()."""
    original_playwright_mock = tool_manager.playwright
    mock_browser_obj = AsyncMock()
    original_playwright_mock.chromium.launch = AsyncMock(
        return_value=mock_browser_obj)
    mock_browser_obj.new_context.side_effect = \
        Exception("Generic New Context Failed")
    mock_browser_obj.is_connected = MagicMock(return_value=True)

    result = await tool_manager.launch_browser(browser_name='chromium')

    assert "Error creating browser context: Generic New Context Failed" in result
    assert tool_manager.browser is None # Browser should be cleaned up
    assert tool_manager.context is None
    mock_browser_obj.close.assert_called_once() # Ensure browser is closed
    original_playwright_mock.stop.assert_called_once() # Ensure playwright is stopped
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_launch_browser_already_running(tool_manager):
    """Test attempting to launch a browser when one is already running."""
    tool_manager.browser = AsyncMock()  # Simulate browser already active
    result = await tool_manager.launch_browser(browser_name='chromium')
    assert "Browser is already running" in result


@pytest.mark.asyncio
async def test_launch_browser_unsupported_browser(tool_manager):
    """Test attempting to launch an unsupported browser."""
    tool_manager.browser = None  # Ensure no browser is "running"
    result = await tool_manager.launch_browser(browser_name='explorer')
    assert "Unsupported browser: explorer" in result


@pytest.mark.asyncio
@patch('mcp_server.tool_manager.async_playwright')
async def test_launch_browser_playwright_start_fails(
        mock_async_playwright_global, tool_manager):
    """Test error handling when async_playwright().start() fails with PlaywrightError."""
    tool_manager.playwright = None  # Ensure playwright is None
    mock_async_playwright_global.return_value.start.side_effect = \
        PlaywrightError("Playwright Start Failed") # Using PlaywrightError
    result = await tool_manager.launch_browser(browser_name='chromium')
    assert "Error starting Playwright: Playwright Start Failed" in result
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_launch_browser_browser_launch_fails(tool_manager):
    """Test error handling when browser.launch() fails."""
    original_playwright_mock = tool_manager.playwright  # Store the mock
    tool_manager.browser = None  # Ensure browser is not set initially
    original_playwright_mock.chromium.launch.side_effect = \
        PlaywrightError("Launch Failed")
    result = await tool_manager.launch_browser(browser_name='chromium')
    assert "Playwright Error launching browser chromium: Launch Failed" in result
    assert tool_manager.browser is None
    assert tool_manager.context is None
    original_playwright_mock.stop.assert_called_once()
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_shutdown_full_cleanup(tool_manager):
    """Test successful closing of all resources."""
    mock_page = AsyncMock()
    mock_page.is_closed = MagicMock(return_value=False)  # Sync mock
    mock_context = AsyncMock()
    mock_browser = AsyncMock()
    tool_manager.page = mock_page
    tool_manager.context = mock_context
    tool_manager.browser = mock_browser
    playwright_mock_instance = tool_manager.playwright  # Save the mock
    result = await tool_manager.shutdown()
    assert "Browser and related resources closed successfully" in result
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    playwright_mock_instance.stop.assert_called_once()
    assert tool_manager.page is None
    assert tool_manager.context is None
    assert tool_manager.browser is None
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_shutdown_partial_resources_active(tool_manager):
    """Test closing when only some resources are active."""
    mock_context = AsyncMock()
    mock_browser = AsyncMock()
    tool_manager.context = mock_context
    tool_manager.browser = mock_browser
    playwright_mock_instance = tool_manager.playwright  # Save the mock
    tool_manager.page = None
    result = await tool_manager.shutdown()
    assert "Browser and related resources closed successfully" in result
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    playwright_mock_instance.stop.assert_called_once()
    assert tool_manager.page is None
    assert tool_manager.context is None
    assert tool_manager.browser is None
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_shutdown_no_active_resources(tool_manager):
    """Test shutdown when no resources are active."""
    tool_manager.page = None
    tool_manager.context = None
    tool_manager.browser = None
    tool_manager.playwright = None
    result = await tool_manager.shutdown()
    assert "No active browser or Playwright instance to close" in result


@pytest.mark.asyncio
async def test_shutdown_handles_playwright_close_errors(tool_manager):
    """Test that shutdown continues and logs if a Playwright close operation fails."""
    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_browser = AsyncMock()
    tool_manager.page = mock_page
    tool_manager.context = mock_context
    tool_manager.browser = mock_browser
    mock_page.is_closed = MagicMock(return_value=False) # Sync mock
    mock_page.close.side_effect = PlaywrightError("Page close failed")
    mock_context.close.side_effect = PlaywrightError("Context close failed")
    mock_browser.close.side_effect = PlaywrightError("Browser close failed")
    tool_manager.playwright.stop.side_effect = \
        PlaywrightError("Playwright stop failed")

    with patch('mcp_server.tool_manager.logger') as mock_logger:
        result = await tool_manager.shutdown()
        assert "Browser and related resources closed successfully" in result
        mock_logger.warning.assert_any_call(
            "Failed to close page (PWE): %s", ANY)
        mock_logger.warning.assert_any_call(
            "Failed to close context (PWE): %s", ANY)
        mock_logger.warning.assert_any_call(
            "Failed to close browser (PWE): %s", ANY)
        mock_logger.warning.assert_any_call(
            "Failed to stop Playwright (PWE): %s", ANY)

    assert tool_manager.page is None
    assert tool_manager.context is None
    assert tool_manager.browser is None
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_shutdown_handles_generic_close_errors(tool_manager):
    """Test shutdown with generic Exceptions during resource closing."""
    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_browser = AsyncMock()
    tool_manager.page = mock_page
    tool_manager.context = mock_context
    tool_manager.browser = mock_browser
    tool_manager.playwright = AsyncMock() # Ensure playwright object exists

    mock_page.is_closed = MagicMock(return_value=False)
    mock_page.close.side_effect = Exception("Generic Page close failed")
    mock_context.close.side_effect = Exception("Generic Context close failed")
    mock_browser.close.side_effect = Exception("Generic Browser close failed")
    tool_manager.playwright.stop.side_effect = Exception("Generic Playwright stop failed")

    with patch('mcp_server.tool_manager.logger') as mock_logger:
        result = await tool_manager.shutdown()
        assert "Browser and related resources closed successfully" in result
        mock_logger.error.assert_any_call(
            "Failed to close page (Exception): %s", "Generic Page close failed")
        mock_logger.error.assert_any_call(
            "Failed to close context (Exception): %s", "Generic Context close failed")
        mock_logger.error.assert_any_call(
            "Failed to close browser (Exception): %s", "Generic Browser close failed")
        mock_logger.error.assert_any_call(
            "Failed to stop Playwright (Exception): %s", "Generic Playwright stop failed")

    assert tool_manager.page is None
    assert tool_manager.context is None
    assert tool_manager.browser is None
    assert tool_manager.playwright is None


@pytest.mark.asyncio
async def test_new_page_success(tool_manager):
    """Test successful creation of a new page."""
    tool_manager.context = AsyncMock()
    tool_manager.page = None
    mock_new_page_instance = AsyncMock()
    tool_manager.context.new_page = AsyncMock(
        return_value=mock_new_page_instance)
    result = await tool_manager.new_page()
    assert "New page created successfully" in result
    tool_manager.context.new_page.assert_called_once()
    assert tool_manager.page == mock_new_page_instance


@pytest.mark.asyncio
async def test_new_page_closes_existing_page(tool_manager):
    """Test that an existing page is closed before a new one is created."""
    tool_manager.context = AsyncMock()
    mock_existing_page = AsyncMock()
    mock_existing_page.is_closed = MagicMock(return_value=False) # Sync mock
    tool_manager.page = mock_existing_page
    mock_new_page_instance = AsyncMock()
    tool_manager.context.new_page = AsyncMock(
        return_value=mock_new_page_instance)
    result = await tool_manager.new_page()
    assert "New page created successfully" in result
    mock_existing_page.close.assert_called_once()
    tool_manager.context.new_page.assert_called_once()
    assert tool_manager.page == mock_new_page_instance


@pytest.mark.asyncio
async def test_new_page_close_existing_page_generic_exception(tool_manager):
    """Test generic Exception when closing an existing page during new_page."""
    tool_manager.context = AsyncMock() # Needs context to attempt new_page
    mock_existing_page = AsyncMock()
    mock_existing_page.is_closed = MagicMock(return_value=False)
    mock_existing_page.close.side_effect = Exception("Generic Close Failed")
    tool_manager.page = mock_existing_page

    mock_new_page_instance = AsyncMock()
    tool_manager.context.new_page = AsyncMock(return_value=mock_new_page_instance)

    with patch('mcp_server.tool_manager.logger') as mock_logger:
        result = await tool_manager.new_page()

    assert "New page created successfully" in result # Should still try to create new
    mock_existing_page.close.assert_called_once()
    mock_logger.error.assert_any_call(
        "Error closing existing page (Exception): %s", "Generic Close Failed")
    assert tool_manager.page == mock_new_page_instance # New page is assigned


@pytest.mark.asyncio
async def test_new_page_no_context(tool_manager):
    """Test new_page when browser context is not available."""
    tool_manager.context = None
    result = await tool_manager.new_page()
    assert "Error: Browser context not available. Launch a browser first." \
           in result


@pytest.mark.asyncio
async def test_new_page_creation_fails(tool_manager):
    """Test error handling if context.new_page() fails with PlaywrightError."""
    tool_manager.context = AsyncMock()
    tool_manager.context.new_page.side_effect = \
        PlaywrightError("Page Creation Failed")
    tool_manager.page = None
    result = await tool_manager.new_page()
    assert "Playwright error creating new page: Page Creation Failed" in result
    assert tool_manager.page is None


@pytest.mark.asyncio
async def test_new_page_creation_generic_exception(tool_manager):
    """Test error handling if context.new_page() fails with generic Exception."""
    tool_manager.context = AsyncMock()
    tool_manager.context.new_page.side_effect = \
        Exception("Generic Page Creation Failed")
    tool_manager.page = None
    result = await tool_manager.new_page()
    assert "Error creating new page: Generic Page Creation Failed" in result
    assert tool_manager.page is None


@pytest.mark.asyncio
@pytest.mark.parametrize("headless_param", [True, False])
async def test_launch_browser_success_firefox(tool_manager, headless_param):
    """Test successful launch of Firefox with headless option."""
    tool_manager.playwright = None
    tool_manager.browser = None
    with patch('mcp_server.tool_manager.async_playwright') \
            as mock_async_playwright_global:
        mock_playwright_instance = AsyncMock()
        mock_async_playwright_global.return_value.start = AsyncMock(
            return_value=mock_playwright_instance)
        mock_browser_obj = AsyncMock()
        mock_playwright_instance.firefox.launch = AsyncMock(
            return_value=mock_browser_obj)
        mock_context_obj = AsyncMock()
        mock_browser_obj.new_context = AsyncMock(
            return_value=mock_context_obj)

        result = await tool_manager.launch_browser(browser_name='firefox', headless=headless_param)
        assert "firefox browser launched successfully" in result
        mock_playwright_instance.firefox.launch.assert_called_once_with(
            headless=headless_param)
        assert tool_manager.browser == mock_browser_obj
        assert tool_manager.context == mock_context_obj


@pytest.mark.asyncio
@pytest.mark.parametrize("headless_param", [True, False])
async def test_launch_browser_success_webkit(tool_manager, headless_param):
    """Test successful launch of Webkit with headless option."""
    tool_manager.playwright = None
    tool_manager.browser = None
    with patch('mcp_server.tool_manager.async_playwright') \
            as mock_async_playwright_global:
        mock_playwright_instance = AsyncMock()
        mock_async_playwright_global.return_value.start = AsyncMock(
            return_value=mock_playwright_instance)
        mock_browser_obj = AsyncMock()
        mock_playwright_instance.webkit.launch = AsyncMock(
            return_value=mock_browser_obj)
        mock_context_obj = AsyncMock()
        mock_browser_obj.new_context = AsyncMock(
            return_value=mock_context_obj)

        result = await tool_manager.launch_browser(browser_name='webkit', headless=headless_param)
        assert "webkit browser launched successfully" in result
        mock_playwright_instance.webkit.launch.assert_called_once_with(
            headless=headless_param)
        assert tool_manager.browser == mock_browser_obj
        assert tool_manager.context == mock_context_obj

