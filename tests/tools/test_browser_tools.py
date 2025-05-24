"""Tests for browser manipulation tools in ToolManager."""
import pytest
from unittest.mock import MagicMock, patch, ANY

# For simulating Playwright errors
from playwright.sync_api import Error as PlaywrightError
from mcp_server.tool_manager import ToolManager  # Import ToolManager


@pytest.fixture
def tool_manager():
    """Provides a fresh ToolManager instance for each test."""
    tm = ToolManager()
    # Prevent actual Playwright calls during most tests by default
    tm.playwright = MagicMock()
    return tm


def test_launch_browser_success_chromium(tool_manager):
    """Test successful launch of Chromium."""
    tool_manager.playwright = None  # Intentionally None to test auto-start
    with patch('mcp_server.tool_manager.sync_playwright') \
            as mock_sync_playwright_global:
        mock_playwright_instance = MagicMock()
        mock_sync_playwright_global.return_value.start.return_value = \
            mock_playwright_instance
        mock_browser_obj = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = \
            mock_browser_obj
        mock_context_obj = MagicMock()
        mock_browser_obj.new_context.return_value = mock_context_obj

        result = tool_manager.launch_browser(browser_name='chromium',
                                             headless=True)

        assert "chromium browser launched successfully" in result
        mock_sync_playwright_global.return_value.start.assert_called_once()
        mock_playwright_instance.chromium.launch.assert_called_once_with(
            headless=True)
        assert tool_manager.browser == mock_browser_obj
        mock_browser_obj.new_context.assert_called_once()
        assert tool_manager.context == mock_context_obj


@patch('mcp_server.tool_manager.sync_playwright')
def test_launch_browser_starts_playwright_if_none(
        mock_sync_playwright_global, tool_manager):
    """Test that Playwright is started if tool_manager.playwright is None."""
    tool_manager.playwright = None  # Explicitly set to None
    mock_playwright_started_instance = MagicMock()
    mock_sync_playwright_global.return_value.start.return_value = \
        mock_playwright_started_instance
    mock_browser_obj = MagicMock()
    mock_playwright_started_instance.chromium.launch.return_value = \
        mock_browser_obj
    mock_context_obj = MagicMock()
    mock_browser_obj.new_context.return_value = mock_context_obj

    result = tool_manager.launch_browser(browser_name='chromium',
                                         headless=True)

    mock_sync_playwright_global.return_value.start.assert_called_once()
    assert tool_manager.playwright == mock_playwright_started_instance
    mock_playwright_started_instance.chromium.launch.assert_called_once_with(
        headless=True)
    assert "chromium browser launched successfully" in result
    assert tool_manager.browser is not None
    assert tool_manager.context is not None


def test_launch_browser_already_running(tool_manager):
    """Test attempting to launch a browser when one is already running."""
    tool_manager.browser = MagicMock()  # Simulate browser already active
    result = tool_manager.launch_browser(browser_name='chromium')
    assert "Browser is already running" in result


def test_launch_browser_unsupported_browser(tool_manager):
    """Test attempting to launch an unsupported browser."""
    tool_manager.browser = None  # Ensure no browser is "running"
    result = tool_manager.launch_browser(browser_name='explorer')
    assert "Unsupported browser: explorer" in result


@patch('mcp_server.tool_manager.sync_playwright')
def test_launch_browser_playwright_start_fails(
        mock_sync_playwright_global, tool_manager):
    """Test error handling when sync_playwright().start() fails."""
    tool_manager.playwright = None  # Ensure playwright is None
    mock_sync_playwright_global.return_value.start.side_effect = \
        Exception("Playwright Start Failed")
    result = tool_manager.launch_browser(browser_name='chromium')
    assert "Error starting Playwright: Playwright Start Failed" in result
    assert tool_manager.playwright is None


def test_launch_browser_browser_launch_fails(tool_manager):
    """Test error handling when browser.launch() fails."""
    original_playwright_mock = tool_manager.playwright  # Store the mock
    tool_manager.browser = None  # Ensure browser is not set initially
    original_playwright_mock.chromium.launch.side_effect = \
        PlaywrightError("Launch Failed")
    result = tool_manager.launch_browser(browser_name='chromium')
    assert "Playwright Error launching browser chromium: Launch Failed" in result
    assert tool_manager.browser is None
    assert tool_manager.context is None
    original_playwright_mock.stop.assert_called_once()
    assert tool_manager.playwright is None


def test_shutdown_full_cleanup(tool_manager):
    """Test successful closing of all resources."""
    mock_page = MagicMock()
    mock_page.is_closed.return_value = False  # Ensure page is seen as open
    mock_context = MagicMock()
    mock_browser = MagicMock()
    tool_manager.page = mock_page
    tool_manager.context = mock_context
    tool_manager.browser = mock_browser
    playwright_mock_instance = tool_manager.playwright  # Save the mock
    result = tool_manager.shutdown()
    assert "Browser and related resources closed successfully" in result
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    playwright_mock_instance.stop.assert_called_once()
    assert tool_manager.page is None
    assert tool_manager.context is None
    assert tool_manager.browser is None
    assert tool_manager.playwright is None


def test_shutdown_partial_resources_active(tool_manager):
    """Test closing when only some resources are active."""
    mock_context = MagicMock()
    mock_browser = MagicMock()
    tool_manager.context = mock_context
    tool_manager.browser = mock_browser
    playwright_mock_instance = tool_manager.playwright  # Save the mock
    tool_manager.page = None
    result = tool_manager.shutdown()
    assert "Browser and related resources closed successfully" in result
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    playwright_mock_instance.stop.assert_called_once()
    assert tool_manager.page is None
    assert tool_manager.context is None
    assert tool_manager.browser is None
    assert tool_manager.playwright is None


def test_shutdown_no_active_resources(tool_manager):
    """Test shutdown when no resources are active."""
    tool_manager.page = None
    tool_manager.context = None
    tool_manager.browser = None
    tool_manager.playwright = None
    result = tool_manager.shutdown()
    assert "No active browser or Playwright instance to close" in result


def test_shutdown_handles_close_errors(tool_manager):
    """Test that shutdown continues and logs if a close operation fails."""
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()
    tool_manager.page = mock_page
    tool_manager.context = mock_context
    tool_manager.browser = mock_browser
    mock_page.is_closed.return_value = False
    mock_page.close.side_effect = PlaywrightError("Page close failed")
    mock_context.is_closed.return_value = False
    mock_context.close.side_effect = PlaywrightError("Context close failed")
    mock_browser.is_closed.return_value = False
    mock_browser.close.side_effect = PlaywrightError("Browser close failed")
    tool_manager.playwright.stop.side_effect = \
        PlaywrightError("Playwright stop failed")

    with patch('mcp_server.tool_manager.logger') as mock_logger:
        result = tool_manager.shutdown()
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


def test_new_page_success(tool_manager):
    """Test successful creation of a new page."""
    tool_manager.context = MagicMock()
    tool_manager.page = None
    mock_new_page_instance = MagicMock()
    tool_manager.context.new_page.return_value = mock_new_page_instance
    result = tool_manager.new_page()
    assert "New page created successfully" in result
    tool_manager.context.new_page.assert_called_once()
    assert tool_manager.page == mock_new_page_instance


def test_new_page_closes_existing_page(tool_manager):
    """Test that an existing page is closed before a new one is created."""
    tool_manager.context = MagicMock()
    mock_existing_page = MagicMock()
    mock_existing_page.is_closed.return_value = False
    tool_manager.page = mock_existing_page
    mock_new_page_instance = MagicMock()
    tool_manager.context.new_page.return_value = mock_new_page_instance
    result = tool_manager.new_page()
    assert "New page created successfully" in result
    mock_existing_page.close.assert_called_once()
    tool_manager.context.new_page.assert_called_once()
    assert tool_manager.page == mock_new_page_instance


def test_new_page_no_context(tool_manager):
    """Test new_page when browser context is not available."""
    tool_manager.context = None
    result = tool_manager.new_page()
    assert "Error: Browser context not available. Launch a browser first." \
           in result


def test_new_page_creation_fails(tool_manager):
    """Test error handling if context.new_page() fails."""
    tool_manager.context = MagicMock()
    tool_manager.context.new_page.side_effect = \
        PlaywrightError("Page Creation Failed")
    tool_manager.page = None
    result = tool_manager.new_page()
    assert "Playwright error creating new page: Page Creation Failed" in result
    assert tool_manager.page is None


def test_launch_browser_success_firefox(tool_manager):
    """Test successful launch of Firefox."""
    tool_manager.playwright = None
    tool_manager.browser = None
    with patch('mcp_server.tool_manager.sync_playwright') \
            as mock_sync_playwright_global:
        mock_playwright_instance = MagicMock()
        mock_sync_playwright_global.return_value.start.return_value = \
            mock_playwright_instance
        mock_browser_obj = MagicMock()
        mock_playwright_instance.firefox.launch.return_value = \
            mock_browser_obj
        mock_context_obj = MagicMock()
        mock_browser_obj.new_context.return_value = mock_context_obj

        result = tool_manager.launch_browser(browser_name='firefox')
        assert "firefox browser launched successfully" in result
        mock_playwright_instance.firefox.launch.assert_called_once_with(
            headless=True)
        assert tool_manager.browser == mock_browser_obj
        assert tool_manager.context == mock_context_obj


def test_launch_browser_success_webkit(tool_manager):
    """Test successful launch of Webkit."""
    tool_manager.playwright = None
    tool_manager.browser = None
    with patch('mcp_server.tool_manager.sync_playwright') \
            as mock_sync_playwright_global:
        mock_playwright_instance = MagicMock()
        mock_sync_playwright_global.return_value.start.return_value = \
            mock_playwright_instance
        mock_browser_obj = MagicMock()
        mock_playwright_instance.webkit.launch.return_value = \
            mock_browser_obj
        mock_context_obj = MagicMock()
        mock_browser_obj.new_context.return_value = mock_context_obj

        result = tool_manager.launch_browser(browser_name='webkit')
        assert "webkit browser launched successfully" in result
        mock_playwright_instance.webkit.launch.assert_called_once_with(
            headless=True)
        assert tool_manager.browser == mock_browser_obj
        assert tool_manager.context == mock_context_obj


def test_new_page_existing_page_already_closed(tool_manager):
    """Test new_page when existing page is already closed."""
    tool_manager.context = MagicMock()
    mock_existing_page = MagicMock()
    mock_existing_page.is_closed.return_value = True
    tool_manager.page = mock_existing_page
    mock_new_page_instance = MagicMock()
    tool_manager.context.new_page.return_value = mock_new_page_instance
    result = tool_manager.new_page()
    assert "New page created successfully" in result
    mock_existing_page.close.assert_not_called()
    tool_manager.context.new_page.assert_called_once()
    assert tool_manager.page == mock_new_page_instance
