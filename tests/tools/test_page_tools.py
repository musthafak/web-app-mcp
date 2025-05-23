import pytest
from unittest.mock import MagicMock, patch
from mcp_server.tools import page_tools
from playwright.sync_api import Error as PlaywrightError # For simulating Playwright errors
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError # For navigation timeout

# Mock the MCPServer class structure for attributes, focusing on 'page'
class MockMCPServer:
    def __init__(self):
        self.page = None # This will be a MagicMock instance in tests

@pytest.fixture
def mock_mcp_server():
    """Provides a fresh mock MCPServer instance for each test."""
    server = MockMCPServer()
    server.page = MagicMock() # Default to having a mocked page object
    return server

@pytest.fixture
def mock_mcp_server_no_page():
    """Provides a mock MCPServer instance where page is initially None."""
    server = MockMCPServer()
    # server.page remains None
    return server

# Tests for goto_page
def test_goto_page_success(mock_mcp_server):
    url = "https://example.com"
    result = page_tools.goto_page(mock_mcp_server, url)
    mock_mcp_server.page.goto.assert_called_once_with(url)
    assert f"Navigation to {url} successful." in result

def test_goto_page_no_page_initialized(mock_mcp_server_no_page):
    result = page_tools.goto_page(mock_mcp_server_no_page, "https://example.com")
    assert "Error: Page not initialized. Call 'new_page' first." in result
    # mock_mcp_server_no_page.page is None, so no goto method to check

def test_goto_page_playwright_navigation_error(mock_mcp_server):
    url = "https://example.com"
    mock_mcp_server.page.goto.side_effect = PlaywrightError("Navigation failed")
    result = page_tools.goto_page(mock_mcp_server, url)
    assert f"Playwright navigation error to {url}: Navigation failed" in result

def test_goto_page_playwright_timeout_error(mock_mcp_server):
    url = "https://example.com"
    # In Playwright, navigation timeouts are typically a specific type of PlaywrightError
    # or can be simulated with a generic PlaywrightError for unit testing if not distinguished by type by the tool.
    # Let's assume PlaywrightError covers it based on current tool implementation.
    # If the tool specifically caught PlaywrightTimeoutError, we'd use that.
    mock_mcp_server.page.goto.side_effect = PlaywrightError("Timeout during navigation") # Simulating general Playwright error
    result = page_tools.goto_page(mock_mcp_server, url)
    assert f"Playwright navigation error to {url}: Timeout during navigation" in result

def test_goto_page_general_exception(mock_mcp_server):
    url = "https://example.com"
    mock_mcp_server.page.goto.side_effect = Exception("Unexpected error")
    result = page_tools.goto_page(mock_mcp_server, url)
    assert f"Error navigating to {url}: Unexpected error" in result

# Tests for capture_screenshot
def test_capture_screenshot_success(mock_mcp_server):
    path = "/screenshots/test.png"
    result = page_tools.capture_screenshot(mock_mcp_server, path)
    mock_mcp_server.page.screenshot.assert_called_once_with(path=path)
    assert f"Screenshot saved to {path}." in result

def test_capture_screenshot_no_page_initialized(mock_mcp_server_no_page):
    result = page_tools.capture_screenshot(mock_mcp_server_no_page, "/screenshots/test.png")
    assert "Error: Page not initialized. Call 'new_page' first." in result

def test_capture_screenshot_playwright_error(mock_mcp_server):
    path = "/screenshots/test.png"
    mock_mcp_server.page.screenshot.side_effect = PlaywrightError("Screenshot failed")
    result = page_tools.capture_screenshot(mock_mcp_server, path)
    assert f"Playwright error capturing screenshot to {path}: Screenshot failed" in result

def test_capture_screenshot_general_exception(mock_mcp_server):
    path = "/screenshots/test.png"
    mock_mcp_server.page.screenshot.side_effect = Exception("Disk full")
    result = page_tools.capture_screenshot(mock_mcp_server, path)
    assert f"Error capturing screenshot to {path}: Disk full" in result

# Tests for close_page
def test_close_page_success(mock_mcp_server):
    mock_page_instance = mock_mcp_server.page # Capture the mock object
    mock_page_instance.is_closed.return_value = False # Page is initially open
    
    result = page_tools.close_page(mock_mcp_server)
    
    mock_page_instance.close.assert_called_once()
    assert mock_mcp_server.page is None
    assert "Page closed successfully." in result

def test_close_page_already_none(mock_mcp_server_no_page):
    result = page_tools.close_page(mock_mcp_server_no_page)
    assert "No active page to close." in result
    assert mock_mcp_server_no_page.page is None 

def test_close_page_already_closed_on_playwright_side(mock_mcp_server):
    mock_page_instance = mock_mcp_server.page # Capture the mock object
    mock_page_instance.is_closed.return_value = True # Playwright says page is closed
    
    result = page_tools.close_page(mock_mcp_server)
    
    mock_page_instance.close.assert_not_called() # Should not call close again
    assert mock_mcp_server.page is None 
    assert "Page closed successfully." in result 

def test_close_page_playwright_error_on_close(mock_mcp_server):
    mock_page_instance = mock_mcp_server.page # Capture the mock object
    mock_page_instance.is_closed.return_value = False
    mock_page_instance.close.side_effect = PlaywrightError("Failed to close page via Playwright")
    
    result = page_tools.close_page(mock_mcp_server)
    
    assert "Playwright error closing page: Failed to close page via Playwright" in result
    assert mock_mcp_server.page is None 

def test_close_page_general_exception_on_close(mock_mcp_server):
    mock_page_instance = mock_mcp_server.page # Capture the mock object
    mock_page_instance.is_closed.return_value = False
    mock_page_instance.close.side_effect = Exception("Unexpected error during close")
    
    result = page_tools.close_page(mock_mcp_server)
    
    assert "Error closing page: Unexpected error during close" in result
    assert mock_mcp_server.page is None
