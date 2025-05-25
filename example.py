"""
Example client script to interact with the MCP Server.

This script demonstrates a sequence of browser automation tasks:
1. Connect to the MCP server.
2. Launch a browser.
3. Create a new page.
4. Navigate to a URL.
5. Extract text content.
6. Capture a screenshot.
7. Close the page and browser.
"""

import asyncio
import logging

from fastmcp import Client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SERVER_ADDRESS = "http://127.0.0.1:8000/sse"


async def main() -> None:
    """
    Runs the main client automation sequence.

    This function attempts to connect to the MCP server and run the browser
    automation demo if the connection is successful.
    """
    logger.info("Attempting to connect to MCP server at %s", SERVER_ADDRESS)
    logger.info("Attempting to connect to MCP server at %s", SERVER_ADDRESS)
    try:
        async with Client(SERVER_ADDRESS) as client:
            logger.info("Successfully connected to MCP server.")

            # Execute the demonstration workflow
            await demo_browser_automation(client)

    except ConnectionRefusedError:
        logger.error(
            "Connection to MCP server at %s refused. Ensure the server is running.",
            SERVER_ADDRESS,
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error("An unexpected error occurred: %s", e, exc_info=True)


async def demo_browser_automation(client: Client) -> None:
    """
    Demonstrate a complete browser automation workflow.

    This function showcases various browser automation capabilities including
    navigation, form interaction, dropdown selection, hover interactions, and
    element capture.

    Args:
        client (Client): An instance of the MCP Client for browser automation.
    """
    # Launch browser and create page
    if not await launch_browser_and_page(client):
        return

    # Perform various demonstrations
    target_url = "https://the-internet.herokuapp.com/"
    await navigate_and_inspect_page(client, target_url)
    await demo_login_form(client, target_url)
    await demo_dropdown_interaction(client, target_url)
    await demo_hover_interaction(client, target_url)
    await capture_multiple_elements(client, target_url)

    # Clean up resources
    await close_resources(client)


async def launch_browser_and_page(client: Client) -> bool:
    """
    Launch a browser instance and create a new page.

    This function first launches a browser, then creates a new page.
    If either operation fails, it cleans up resources as needed.

    Args:
        client (Client): An instance of the MCP Client.

    Returns:
        bool: True if both operations succeeded, False otherwise.
    """
    # 1. Launch a browser
    logger.info("Requesting to launch browser...")
    launch_params = {"browser_name": "chromium", "headless": False}
    launch_result = await client.call_tool("launch_browser", launch_params)
    logger.info("Launch browser result: %s", launch_result)
    if "error" in str(launch_result).lower():
        logger.error("Failed to launch browser. Exiting.")
        return False

    # 2. Create a new page
    logger.info("Requesting to create a new page...")
    new_page_result = await client.call_tool("new_page", {})
    logger.info("New page result: %s", new_page_result)
    if "error" in str(new_page_result).lower():
        logger.error("Failed to create new page. Closing browser.")
        close_browser_result = await client.call_tool("close_browser", {})
        logger.info("Close browser result: %s", close_browser_result)
        return False

    return True


async def navigate_and_inspect_page(client: Client, target_url: str) -> None:
    """
    Navigate to a URL and inspect page properties.

    This function navigates to the specified URL and retrieves information
    about the page including its current URL, title, and accessibility tree.

    Args:
        client (Client): An instance of the MCP Client.
        target_url (str): The URL to navigate to.
    """
    logger.info("Requesting to navigate to %s...", target_url)
    goto_result = await client.call_tool("goto_page", {"url": target_url})
    logger.info("Goto page result: %s", goto_result)

    if "error" in str(goto_result).lower():
        logger.error("Failed to navigate to %s.", target_url)
        return

    # Get page information
    current_url_result = await client.call_tool("get_current_url", {})
    logger.info("Get current URL result: %s", current_url_result)

    page_title_result = await client.call_tool("get_page_title", {})
    logger.info("Get page title result: %s", page_title_result)

    # Capture page accessibility tree
    logger.info("Requesting full page AOM snapshot...")
    page_aom_snapshot_result = await client.call_tool("capture_area_snapshot", {})

    # Log a summary, as the full snapshot can be very large
    logger.info("Full page AOM snapshot result: %s", page_aom_snapshot_result)


async def demo_login_form(  # pylint: disable=too-many-locals
    client: Client, target_url: str
) -> None:
    """
    Demonstrate interacting with a login form.

    This function navigates to a login page, fills in username and password fields,
    retrieves form element attributes and HTML, and submits the form.

    Args:
        client (Client): An instance of the MCP Client.
        target_url (str): The base URL.
    """
    login_url = target_url + "login"
    logger.info("Requesting to navigate to %s...", login_url)
    goto_login_result = await client.call_tool("goto_page", {"url": login_url})
    logger.info("Goto page result: %s", goto_login_result)

    if "error" in str(goto_login_result).lower():
        return

    logger.info("Interacting with login form elements...")
    await client.call_tool("wait_for_selector", {"selector": "#username"})
    logger.info("Waited for #username selector.")

    # Fill username field
    fill_username_params = {"selector": "#username", "text": "tomsmith"}
    fill_username_result = await client.call_tool("fill_element", fill_username_params)
    logger.info("Fill username result: %s", fill_username_result)

    # Fill password field
    fill_password_params = {
        "selector": "#password",
        "text": "SuperSecretPassword!",
    }
    fill_password_result = await client.call_tool("fill_element", fill_password_params)
    logger.info("Fill password result: %s", fill_password_result)

    # Get attribute example
    get_attribute_params = {
        "selector": "#username",
        "attribute_name": "type",
    }
    get_attribute_result = await client.call_tool(
        "get_element_attribute", get_attribute_params
    )
    logger.info(
        "Get attribute 'type' for #username result: %s",
        get_attribute_result,
    )

    # Get HTML example
    get_form_html_params = {
        "selector": "form#login",
        "char_limit": 200,
        "remove_scripts": True,
    }
    get_form_html_result = await client.call_tool(
        "get_element_html", get_form_html_params
    )
    logger.info(
        "Get HTML for form#login (truncated, scripts removed) result: %s",
        get_form_html_result,
    )

    # Get bounding box example
    bounding_box_params = {"selector": "button[type='submit']"}
    bounding_box_result = await client.call_tool(
        "get_element_bounding_box", bounding_box_params
    )
    logger.info(
        "Get bounding box for login button result: %s",
        bounding_box_result,
    )

    # Capture element accessibility tree
    button_aom_params = {"selector": "button[type='submit']"}
    button_aom_result = await client.call_tool(
        "capture_area_snapshot", button_aom_params
    )

    logger.info("Login button AOM snapshot result: %s", button_aom_result)

    # Click the login button
    await submit_login_form(client)


async def submit_login_form(client: Client) -> None:
    """
    Submit the login form and handle post-login navigation.

    This function clicks the login button, waits for navigation to complete,
    and logs the current URL after the login attempt.

    Args:
        client (Client): An instance of the MCP Client.
    """
    click_login_params = {"selector": "button[type='submit']"}
    click_login_result = await client.call_tool("click_element", click_login_params)
    logger.info("Click login button result: %s", click_login_result)

    # Wait for navigation after login
    logger.info("Waiting for navigation after login click...")
    wait_nav_params = {
        "url": "**/secure",
        "timeout": 5,
        "wait_until": "load",
    }  # wait up to 5s for URL containing /secure
    nav_after_login_result = await client.call_tool(
        "wait_for_navigation", wait_nav_params
    )
    logger.info(
        "Wait for navigation after login result: %s",
        nav_after_login_result,
    )

    # Log current URL after attempted login
    current_url_after_login = await client.call_tool("get_current_url", {})
    logger.info("Current URL after login attempt: %s", current_url_after_login)


async def demo_dropdown_interaction(client: Client, target_url: str) -> None:
    """
    Demonstrate interaction with dropdown elements.

    This function navigates to a dropdown page and demonstrates selecting
    options by both value and label.

    Args:
        client (Client): An instance of the MCP Client.
        target_url (str): The base URL.
    """
    dropdown_url = target_url + "dropdown"
    logger.info("Requesting to navigate to %s...", dropdown_url)
    goto_dropdown_result = await client.call_tool("goto_page", {"url": dropdown_url})
    logger.info("Goto page result: %s", goto_dropdown_result)

    if "error" in str(goto_dropdown_result).lower():
        return

    dropdown_selector = "#dropdown"
    logger.info("Waiting for dropdown selector %s...", dropdown_selector)
    await client.call_tool("wait_for_selector", {"selector": dropdown_selector})
    logger.info("Waited for %s selector.", dropdown_selector)

    # Select by value
    select_value_params = {
        "selector": dropdown_selector,
        "option_value": "1",
    }
    select_value_result = await client.call_tool("select_option", select_value_params)
    logger.info("Select option by value '1' result: %s", select_value_result)

    # Select by label
    select_label_params = {
        "selector": dropdown_selector,
        "option_label": "Option 2",
    }
    select_label_result = await client.call_tool("select_option", select_label_params)
    logger.info(
        "Select option by label 'Option 2' result: %s",
        select_label_result,
    )


async def demo_hover_interaction(client: Client, target_url: str) -> None:
    """
    Demonstrate hover interactions on elements.

    This function navigates to a page with hover effects, performs a hover action
    on an element, and retrieves the text content that appears after hovering.

    Args:
        client (Client): An instance of the MCP Client.
        target_url (str): The base URL.
    """
    hovers_url = target_url + "hovers"
    logger.info("Requesting to navigate to %s...", hovers_url)
    goto_hovers_result = await client.call_tool("goto_page", {"url": hovers_url})
    logger.info("Goto page result: %s", goto_hovers_result)

    if "error" in str(goto_hovers_result).lower():
        return

    # Hover over the first user profile to reveal its caption
    first_figure_selector = ".figure:nth-of-type(1)"
    logger.info("Waiting for figure selector %s...", first_figure_selector)
    await client.call_tool("wait_for_selector", {"selector": first_figure_selector})
    logger.info("Waited for %s selector.", first_figure_selector)

    hover_params = {"selector": first_figure_selector}
    hover_result = await client.call_tool("hover_element", hover_params)
    logger.info("Hover element result: %s", hover_result)

    # Wait for the caption to be visible and get its text
    caption_selector = f"{first_figure_selector} .figcaption h5"
    logger.info(
        "Waiting for caption selector %s to be visible...",
        caption_selector,
    )
    await client.call_tool("wait_for_selector", {"selector": caption_selector})
    logger.info("Waited for %s selector to be visible.", caption_selector)

    caption_text_params = {"selector": caption_selector}
    caption_text_result = await client.call_tool(
        "get_text_content", caption_text_params
    )
    logger.info("Get text content of revealed caption: %s", caption_text_result)


async def capture_multiple_elements(client: Client, target_url: str) -> None:
    """
    Demonstrate capturing multiple elements on a page.

    This function navigates to the main page, captures all link elements within
    list items, and takes a final screenshot of the viewport.

    Args:
        client (Client): An instance of the MCP Client.
        target_url (str): The URL to navigate to.
    """
    logger.info(
        "Navigating back to main page to capture multiple elements: %s",
        target_url,
    )
    await client.call_tool("goto_page", {"url": target_url})

    capture_links_params = {
        "selector": "ul li a"
    }  # Example: capture all links in lists
    captured_links_result = await client.call_tool(
        "capture_elements", capture_links_params
    )
    if isinstance(captured_links_result, list) and captured_links_result:
        logger.info(
            "Captured %d links. First link text: %s",
            len(captured_links_result),
            captured_links_result,
        )
    else:
        logger.info("Capture elements result: %s", captured_links_result)

    # Take final screenshot
    logger.info("Requesting final viewport screenshot...")
    final_screenshot_result = await client.call_tool("capture_screenshot", {})
    logger.info("Final screenshot result (base64 length): %s", final_screenshot_result)


async def close_resources(client: Client) -> None:
    """
    Clean up by closing the page and browser.

    This function properly terminates the browser automation session by
    closing the active page and then shutting down the browser.

    Args:
        client (Client): An instance of the MCP Client.
    """
    # Close the page
    logger.info("Requesting to close the page...")
    close_page_result = await client.call_tool("close_page", {})
    logger.info("Close page result: %s", close_page_result)

    # Close the browser
    logger.info("Requesting to shutdown the browser...")
    shutdown_result = await client.call_tool("close_browser", {})
    logger.info("Shutdown result: %s", shutdown_result)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
