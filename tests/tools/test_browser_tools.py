import pytest
from unittest.mock import MagicMock, patch
from mcp_server.tools import browser_tools
from playwright.sync_api import Error as PlaywrightError # For simulating Playwright errors

# Mock the MCPServer class structure for attributes
class MockMCPServer:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

@pytest.fixture
def mock_mcp_server():
    """Provides a fresh mock MCPServer instance for each test."""
    return MockMCPServer()

def test_launch_browser_success_chromium(mock_mcp_server):
    """Test successful launch of Chromium."""
    # Playwright itself should be None initially if we test its auto-start
    mock_mcp_server.playwright = None # Intentionally None to test auto-start
    
    # We need to patch 'playwright.sync_api.sync_playwright' as it's imported inside the function
    with patch('playwright.sync_api.sync_playwright') as mock_sync_playwright_global:
        mock_playwright_instance = MagicMock()
        mock_sync_playwright_global.return_value.start.return_value = mock_playwright_instance
        
        mock_browser_obj = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser_obj
        mock_context_obj = MagicMock()
        mock_browser_obj.new_context.return_value = mock_context_obj

        result = browser_tools.launch_browser(mock_mcp_server, browser_name='chromium', headless=True)

        assert "chromium browser launched successfully" in result
        mock_sync_playwright_global.return_value.start.assert_called_once()
        mock_playwright_instance.chromium.launch.assert_called_once_with(headless=True)
        assert mock_mcp_server.browser == mock_browser_obj
        mock_browser_obj.new_context.assert_called_once()
    assert mock_mcp_server.context == mock_context_obj

@patch('playwright.sync_api.sync_playwright') # Patch the actual import location
def test_launch_browser_starts_playwright_if_none(mock_sync_playwright_global, mock_mcp_server):
    """Test that Playwright is started if mcp_server.playwright is None."""
    mock_mcp_server.playwright = None # Explicitly set to None

    mock_playwright_started_instance = MagicMock()
    mock_sync_playwright_global.return_value.start.return_value = mock_playwright_started_instance
    
    mock_browser_obj = MagicMock()
    mock_playwright_started_instance.chromium.launch.return_value = mock_browser_obj
    mock_context_obj = MagicMock()
    mock_browser_obj.new_context.return_value = mock_context_obj

    result = browser_tools.launch_browser(mock_mcp_server, browser_name='chromium', headless=True)

    mock_sync_playwright_global.return_value.start.assert_called_once()
    assert mock_mcp_server.playwright == mock_playwright_started_instance
    mock_playwright_started_instance.chromium.launch.assert_called_once_with(headless=True)
    assert "chromium browser launched successfully" in result
    assert mock_mcp_server.browser is not None # Check that browser is set
    assert mock_mcp_server.context is not None # Check that context is set


def test_launch_browser_already_running(mock_mcp_server):
    """Test attempting to launch a browser when one is already running."""
    mock_mcp_server.browser = MagicMock() # Simulate browser already active
    result = browser_tools.launch_browser(mock_mcp_server, browser_name='chromium')
    assert "Browser is already running" in result

def test_launch_browser_unsupported_browser(mock_mcp_server):
    """Test attempting to launch an unsupported browser."""
    mock_mcp_server.playwright = MagicMock() # Playwright needs to exist for this check
    mock_mcp_server.browser = None # Ensure no browser is "running"
    result = browser_tools.launch_browser(mock_mcp_server, browser_name='explorer')
    assert "Unsupported browser: explorer" in result

@patch('playwright.sync_api.sync_playwright') # Patch the actual import location
def test_launch_browser_playwright_start_fails(mock_sync_playwright_global, mock_mcp_server):
    """Test error handling when sync_playwright().start() fails."""
    mock_mcp_server.playwright = None # Ensure playwright is None to trigger start attempt
    mock_sync_playwright_global.return_value.start.side_effect = Exception("Playwright Start Failed")
    result = browser_tools.launch_browser(mock_mcp_server, browser_name='chromium')
    assert "Error starting Playwright: Playwright Start Failed" in result
    assert mock_mcp_server.playwright is None


def test_launch_browser_browser_launch_fails(mock_mcp_server):
    """Test error handling when browser.launch() fails."""
    original_playwright_mock = MagicMock()
    mock_mcp_server.playwright = original_playwright_mock # Pre-set playwright
    mock_mcp_server.browser = None # Ensure browser is not set initially

    original_playwright_mock.chromium.launch.side_effect = PlaywrightError("Launch Failed")
    
    result = browser_tools.launch_browser(mock_mcp_server, browser_name='chromium')
    
    assert "Playwright Error launching browser chromium: Launch Failed" in result
    assert mock_mcp_server.browser is None
    assert mock_mcp_server.context is None
    # Check if playwright was stopped (on the original mock) and then reset on server
    original_playwright_mock.stop.assert_called_once()
    assert mock_mcp_server.playwright is None


def test_close_browser_full_cleanup(mock_mcp_server):
    """Test successful closing of all resources."""
    # Store mocks locally before they are set to None by close_browser
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()
    mock_playwright = MagicMock()

    mock_mcp_server.page = mock_page
    mock_mcp_server.context = mock_context
    mock_mcp_server.browser = mock_browser
    mock_mcp_server.playwright = mock_playwright

    result = browser_tools.close_browser(mock_mcp_server)

    assert "Browser and related resources closed successfully" in result
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert mock_mcp_server.page is None
    assert mock_mcp_server.context is None
    assert mock_mcp_server.browser is None
    assert mock_mcp_server.playwright is None

def test_close_browser_partial_resources_active(mock_mcp_server):
    """Test closing when only some resources are active (e.g., only browser and context)."""
    mock_context = MagicMock()
    mock_browser = MagicMock()
    
    mock_mcp_server.context = mock_context
    mock_mcp_server.browser = mock_browser
    mock_mcp_server.playwright = None # playwright and page are None
    mock_mcp_server.page = None


    result = browser_tools.close_browser(mock_mcp_server)

    assert "Browser and related resources closed successfully" in result
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    assert mock_mcp_server.page is None 
    assert mock_mcp_server.context is None
    assert mock_mcp_server.browser is None
    assert mock_mcp_server.playwright is None 

def test_close_browser_no_active_resources(mock_mcp_server):
    # Ensure all relevant attributes are None
    mock_mcp_server.page = None
    mock_mcp_server.context = None
    mock_mcp_server.browser = None
    mock_mcp_server.playwright = None
    result = browser_tools.close_browser(mock_mcp_server)
    assert "No active browser or Playwright instance to close" in result

def test_close_browser_handles_close_errors(mock_mcp_server):
    """Test that close_browser continues and logs if a close operation fails."""
    # Store mocks locally
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()
    mock_playwright = MagicMock()

    mock_mcp_server.page = mock_page
    mock_mcp_server.context = mock_context
    mock_mcp_server.browser = mock_browser
    mock_mcp_server.playwright = mock_playwright
    
    mock_page.close.side_effect = Exception("Page close failed")
    mock_context.close.side_effect = Exception("Context close failed")
    mock_browser.close.side_effect = Exception("Browser close failed")
    mock_playwright.stop.side_effect = Exception("Playwright stop failed")

    with patch('mcp_server.tools.browser_tools.logging') as mock_logging:
        result = browser_tools.close_browser(mock_mcp_server)
        assert "Browser and related resources closed successfully" in result 
        mock_logging.warning.assert_any_call("Could not close page: Page close failed")
        mock_logging.warning.assert_any_call("Could not close browser context: Context close failed")
        mock_logging.warning.assert_any_call("Could not close browser: Browser close failed")
        mock_logging.warning.assert_any_call("Could not stop Playwright: Playwright stop failed")

    assert mock_mcp_server.page is None 
    assert mock_mcp_server.context is None
    assert mock_mcp_server.browser is None
    assert mock_mcp_server.playwright is None


def test_new_page_success(mock_mcp_server):
    # Ensure context exists for new page creation
    mock_mcp_server.context = MagicMock() 
    # Ensure page is None initially or will be closed
    mock_mcp_server.page = None 
    """Test successful creation of a new page."""
    
    mock_new_page_instance = MagicMock()
    mock_mcp_server.context.new_page.return_value = mock_new_page_instance

    result = browser_tools.new_page(mock_mcp_server)

    assert "New page created successfully" in result
    mock_mcp_server.context.new_page.assert_called_once()
    assert mock_mcp_server.page == mock_new_page_instance

def test_new_page_closes_existing_page(mock_mcp_server):
    """Test that an existing page is closed before a new one is created."""
    mock_mcp_server.context = MagicMock()
    
    mock_existing_page = MagicMock()
    mock_existing_page.is_closed.return_value = False
    mock_mcp_server.page = mock_existing_page # Set an existing page
    
    mock_new_page_instance = MagicMock()
    mock_mcp_server.context.new_page.return_value = mock_new_page_instance

    result = browser_tools.new_page(mock_mcp_server)

    assert "New page created successfully" in result
    mock_existing_page.close.assert_called_once()
    mock_mcp_server.context.new_page.assert_called_once() # Ensure new page is still created
    assert mock_mcp_server.page == mock_new_page_instance

def test_new_page_no_context(mock_mcp_server): # Renamed fixture for clarity
    """Test new_page when browser context is not available."""
    mock_mcp_server.context = None 
    result = browser_tools.new_page(mock_mcp_server)
    assert "Error: Browser context not available. Launch a browser first." in result

def test_new_page_creation_fails(mock_mcp_server):
    """Test error handling if context.new_page() fails."""
    mock_mcp_server.context = MagicMock()
    mock_mcp_server.context.new_page.side_effect = PlaywrightError("Page Creation Failed")
    mock_mcp_server.page = None # Ensure page is initially None

    result = browser_tools.new_page(mock_mcp_server)
    
    assert "Error creating new page: Page Creation Failed" in result
    assert mock_mcp_server.page is None 
    
# Test for launching firefox and webkit
def test_launch_browser_success_firefox(mock_mcp_server):
    mock_mcp_server.playwright = None # Test auto-start
    mock_mcp_server.browser = None # Ensure browser is not pre-set

    with patch('playwright.sync_api.sync_playwright') as mock_sync_playwright_global:
        mock_playwright_instance = MagicMock()
        mock_sync_playwright_global.return_value.start.return_value = mock_playwright_instance
        
        mock_browser_obj = MagicMock()
        mock_playwright_instance.firefox.launch.return_value = mock_browser_obj
        mock_context_obj = MagicMock()
        mock_browser_obj.new_context.return_value = mock_context_obj

        result = browser_tools.launch_browser(mock_mcp_server, browser_name='firefox')
        assert "firefox browser launched successfully" in result
        mock_playwright_instance.firefox.launch.assert_called_once_with(headless=True)
        assert mock_mcp_server.browser == mock_browser_obj
        assert mock_mcp_server.context == mock_context_obj


def test_launch_browser_success_webkit(mock_mcp_server):
    mock_mcp_server.playwright = None # Test auto-start
    mock_mcp_server.browser = None # Ensure browser is not pre-set

    with patch('playwright.sync_api.sync_playwright') as mock_sync_playwright_global:
        mock_playwright_instance = MagicMock()
        mock_sync_playwright_global.return_value.start.return_value = mock_playwright_instance
        
        mock_browser_obj = MagicMock()
        mock_playwright_instance.webkit.launch.return_value = mock_browser_obj
        mock_context_obj = MagicMock()
        mock_browser_obj.new_context.return_value = mock_context_obj

        result = browser_tools.launch_browser(mock_mcp_server, browser_name='webkit')
        assert "webkit browser launched successfully" in result
        mock_playwright_instance.webkit.launch.assert_called_once_with(headless=True)
        assert mock_mcp_server.browser == mock_browser_obj
        assert mock_mcp_server.context == mock_context_obj


# Test that if mcp_server.page exists and is_closed() is True, it does not call close()
def test_new_page_existing_page_already_closed(mock_mcp_server):
    mock_mcp_server.context = MagicMock() # Context must exist
    
    mock_existing_page = MagicMock()
    mock_existing_page.is_closed.return_value = True 
    mock_mcp_server.page = mock_existing_page # Set an existing, but closed, page
    
    mock_new_page_instance = MagicMock()
    mock_mcp_server.context.new_page.return_value = mock_new_page_instance

    result = browser_tools.new_page(mock_mcp_server)

    assert "New page created successfully" in result
    mock_existing_page.close.assert_not_called() 
    mock_mcp_server.context.new_page.assert_called_once()
    assert mock_mcp_server.page == mock_new_page_instance
