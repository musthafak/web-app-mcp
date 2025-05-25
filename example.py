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

# Configure basic logging for the client
# Using __name__ for the logger name is a common practice.
# However, for a simple script like this, using the root logger is also fine.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SERVER_ADDRESS = "http://127.0.0.1:8000/sse"


async def main():
    """Runs the main client automation sequence."""
    logger.info("Attempting to connect to MCP server at %s", SERVER_ADDRESS)
    try:
        async with Client(SERVER_ADDRESS) as client:
            logger.info("Successfully connected to MCP server.")

            # 1. Launch a browser
            logger.info("Requesting to launch browser...")
            launch_params = {"browser_name": "chromium", "headless": False}
            launch_result = await client.call_tool("launch_browser", launch_params)
            logger.info("Launch browser result: %s", launch_result)
            if "error" in str(launch_result).lower():
                logger.error("Failed to launch browser. Exiting.")
                return

            # 2. Create a new page
            logger.info("Requesting to create a new page...")
            new_page_result = await client.call_tool("new_page", {})
            logger.info("New page result: %s", new_page_result)
            if "error" in str(new_page_result).lower():
                logger.error("Failed to create new page. Closing browser.")
                close_browser_result = await client.call_tool("close_browser", {})
                logger.info("Close browser result: %s", close_browser_result)
                return

            # 3. Navigate to a page
            target_url = "https://the-internet.herokuapp.com/"
            logger.info("Requesting to navigate to %s...", target_url)
            goto_result = await client.call_tool("goto_page", {"url": target_url})
            logger.info("Goto page result: %s", goto_result)
            if "error" in str(goto_result).lower():
                logger.error("Failed to navigate to %s.", target_url)
            else:
                current_url_result = await client.call_tool("get_current_url", {})
                logger.info("Get current URL result: %s", current_url_result)

                page_title_result = await client.call_tool("get_page_title", {})
                logger.info("Get page title result: %s", page_title_result)

                logger.info("Requesting full page AOM snapshot...")
                page_aom_snapshot_params = {}  # No selector for full page
                page_aom_snapshot_result = await client.call_tool(
                    "capture_area_snapshot", page_aom_snapshot_params
                )
                # Log a summary, as the full snapshot can be very large
                if (
                    isinstance(page_aom_snapshot_result, dict)
                    and "role" in page_aom_snapshot_result
                ):
                    logger.info(
                        "Full page AOM snapshot captured successfully (root role: %s).",
                        page_aom_snapshot_result.get("role"),
                    )
                else:
                    logger.info(
                        "Full page AOM snapshot result: %s", page_aom_snapshot_result
                    )

                # Demonstrate Login Form Interaction
                login_url = target_url + "login"
                logger.info("Requesting to navigate to %s...", login_url)
                goto_login_result = await client.call_tool(
                    "goto_page", {"url": login_url}
                )
                logger.info("Goto page result: %s", goto_login_result)
                if "error" not in str(goto_login_result).lower():
                    logger.info("Interacting with login form elements...")
                    await client.call_tool(
                        "wait_for_selector", {"selector": "#username"}
                    )
                    logger.info("Waited for #username selector.")

                    fill_username_params = {"selector": "#username", "text": "tomsmith"}
                    fill_username_result = await client.call_tool(
                        "fill_element", fill_username_params
                    )
                    logger.info("Fill username result: %s", fill_username_result)

                    fill_password_params = {
                        "selector": "#password",
                        "text": "SuperSecretPassword!",
                    }
                    fill_password_result = await client.call_tool(
                        "fill_element", fill_password_params
                    )
                    logger.info("Fill password result: %s", fill_password_result)

                    # Demonstrate get_element_attribute on the username field
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

                    # Demonstrate get_element_html for the form
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

                    # Demonstrate get_element_bounding_box for the login button
                    bounding_box_params = {"selector": "button[type='submit']"}
                    bounding_box_result = await client.call_tool(
                        "get_element_bounding_box", bounding_box_params
                    )
                    logger.info(
                        "Get bounding box for login button result: %s",
                        bounding_box_result,
                    )

                    # Demonstrate capture_area_snapshot for the login button
                    button_aom_params = {"selector": "button[type='submit']"}
                    button_aom_result = await client.call_tool(
                        "capture_area_snapshot", button_aom_params
                    )
                    if (
                        isinstance(button_aom_result, dict)
                        and "role" in button_aom_result
                    ):
                        logger.info(
                            "Login button AOM snapshot captured successfully (role: %s).",
                            button_aom_result.get("role"),
                        )
                    else:
                        logger.info(
                            "Login button AOM snapshot result: %s", button_aom_result
                        )

                    # Click the login button
                    click_login_params = {"selector": "button[type='submit']"}
                    click_login_result = await client.call_tool(
                        "click_element", click_login_params
                    )
                    logger.info("Click login button result: %s", click_login_result)

                    # Wait for navigation after login (to secure page or error message)
                    logger.info("Waiting for navigation after login click...")
                    # Example: wait for a selector on the target page or a general navigation
                    # If login is successful, it navigates to /secure. Let's wait for an element there.
                    # If login fails, it stays on /login. This wait might timeout or succeed if URL changes slightly.
                    # For robustness, one might check current URL or content before deciding to wait for a specific element.
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
                    # Log current URL after attempted login and navigation
                    current_url_after_login = await client.call_tool(
                        "get_current_url", {}
                    )
                    logger.info(
                        "Current URL after login attempt: %s", current_url_after_login
                    )

                # Demonstrate Dropdown Interaction
                dropdown_url = target_url + "dropdown"
                logger.info("Requesting to navigate to %s...", dropdown_url)
                goto_dropdown_result = await client.call_tool(
                    "goto_page", {"url": dropdown_url}
                )
                logger.info("Goto page result: %s", goto_dropdown_result)
                if "error" not in str(goto_dropdown_result).lower():
                    dropdown_selector = "#dropdown"
                    logger.info(
                        "Waiting for dropdown selector %s...", dropdown_selector
                    )
                    await client.call_tool(
                        "wait_for_selector", {"selector": dropdown_selector}
                    )
                    logger.info("Waited for %s selector.", dropdown_selector)

                    # Select by value
                    select_value_params = {
                        "selector": dropdown_selector,
                        "option_value": "1",
                    }
                    select_value_result = await client.call_tool(
                        "select_option", select_value_params
                    )
                    logger.info(
                        "Select option by value '1' result: %s", select_value_result
                    )
                    # Add a small delay or check to observe selection if running non-headless
                    # For headless, we can verify by trying to get the selected option's text if needed

                    # Select by label
                    select_label_params = {
                        "selector": dropdown_selector,
                        "option_label": "Option 2",
                    }
                    select_label_result = await client.call_tool(
                        "select_option", select_label_params
                    )
                    logger.info(
                        "Select option by label 'Option 2' result: %s",
                        select_label_result,
                    )

                # Demonstrate Hover Interaction
                hovers_url = target_url + "hovers"
                logger.info("Requesting to navigate to %s...", hovers_url)
                goto_hovers_result = await client.call_tool(
                    "goto_page", {"url": hovers_url}
                )
                logger.info("Goto page result: %s", goto_hovers_result)
                if "error" not in str(goto_hovers_result).lower():
                    # Hover over the first user profile to reveal its caption
                    first_figure_selector = ".figure:nth-of-type(1)"
                    logger.info(
                        "Waiting for figure selector %s...", first_figure_selector
                    )
                    await client.call_tool(
                        "wait_for_selector", {"selector": first_figure_selector}
                    )
                    logger.info("Waited for %s selector.", first_figure_selector)

                    hover_params = {"selector": first_figure_selector}
                    hover_result = await client.call_tool("hover_element", hover_params)
                    logger.info("Hover element result: %s", hover_result)

                    # After hover, the caption (e.g., "name: user1") should appear.
                    # Wait for the caption to be visible and then get its text.
                    # The selector targets the h5 element within the figcaption of the first figure.
                    caption_selector = f"{first_figure_selector} .figcaption h5"
                    logger.info(
                        "Waiting for caption selector %s to be visible...",
                        caption_selector,
                    )
                    # Note: 'state: "visible"' might be needed if element is present but hidden initially
                    await client.call_tool(
                        "wait_for_selector", {"selector": caption_selector}
                    )
                    logger.info(
                        "Waited for %s selector to be visible.", caption_selector
                    )

                    caption_text_params = {"selector": caption_selector}
                    caption_text_result = await client.call_tool(
                        "get_text_content", caption_text_params
                    )
                    logger.info(
                        "Get text content of revealed caption: %s",
                        (
                            caption_text_result.strip()
                            if isinstance(caption_text_result, str)
                            else caption_text_result
                        ),
                    )

                # The following general calls are now covered by more specific demonstrations above or are out of context.
                # Removing them to streamline the example.

                # Demonstrate Dropdown Interaction
                dropdown_url = target_url + "dropdown"
                logger.info("Requesting to navigate to %s...", dropdown_url)
                goto_dropdown_result = await client.call_tool(
                    "goto_page", {"url": dropdown_url}
                )
                logger.info("Goto page result: %s", goto_dropdown_result)
                if "error" not in str(goto_dropdown_result).lower():
                    dropdown_selector = "#dropdown"
                    logger.info(
                        "Waiting for dropdown selector %s...", dropdown_selector
                    )
                    await client.call_tool(
                        "wait_for_selector", {"selector": dropdown_selector}
                    )
                    logger.info("Waited for %s selector.", dropdown_selector)

                    # Select by value
                    select_value_params = {
                        "selector": dropdown_selector,
                        "option_value": "1",
                    }
                    select_value_result = await client.call_tool(
                        "select_option", select_value_params
                    )
                    logger.info(
                        "Select option by value '1' result: %s", select_value_result
                    )

                    # Select by label
                    select_label_params = {
                        "selector": dropdown_selector,
                        "option_label": "Option 2",
                    }
                    select_label_result = await client.call_tool(
                        "select_option", select_label_params
                    )
                    logger.info(
                        "Select option by label 'Option 2' result: %s",
                        select_label_result,
                    )

                # Demonstrate Hover Interaction
                hovers_url = target_url + "hovers"
                logger.info("Requesting to navigate to %s...", hovers_url)
                goto_hovers_result = await client.call_tool(
                    "goto_page", {"url": hovers_url}
                )
                logger.info("Goto page result: %s", goto_hovers_result)
                if "error" not in str(goto_hovers_result).lower():
                    first_figure_selector = ".figure:nth-of-type(1)"
                    logger.info(
                        "Waiting for figure selector %s...", first_figure_selector
                    )
                    await client.call_tool(
                        "wait_for_selector", {"selector": first_figure_selector}
                    )
                    logger.info("Waited for %s selector.", first_figure_selector)

                    hover_params = {"selector": first_figure_selector}
                    hover_result = await client.call_tool("hover_element", hover_params)
                    logger.info("Hover element result: %s", hover_result)

                    caption_selector = f"{first_figure_selector} .figcaption h5"
                    logger.info(
                        "Waiting for caption selector %s to be visible...",
                        caption_selector,
                    )
                    await client.call_tool(
                        "wait_for_selector", {"selector": caption_selector}
                    )
                    logger.info(
                        "Waited for %s selector to be visible.", caption_selector
                    )

                    caption_text_params = {"selector": caption_selector}
                    caption_text_result = await client.call_tool(
                        "get_text_content", caption_text_params
                    )
                    logger.info(
                        "Get text content of revealed caption: %s",
                        (
                            caption_text_result.strip()
                            if isinstance(caption_text_result, str)
                            else caption_text_result
                        ),
                    )

                # Demonstrate capture_elements (e.g., all links on the main page again)
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

                # Final viewport screenshot
                logger.info("Requesting final viewport screenshot...")
                final_screenshot_result = await client.call_tool(
                    "capture_screenshot", {}
                )
                logger.info(
                    "Final screenshot result (base64 length): %s",
                    (
                        len(final_screenshot_result)
                        if isinstance(final_screenshot_result, str)
                        else final_screenshot_result
                    ),
                )

            # 6. Close the page
            logger.info("Requesting to close the page...")
            close_page_result = await client.call_tool("close_page", {})
            logger.info("Close page result: %s", close_page_result)

            # 7. Close the browser
            logger.info("Requesting to shutdown the browser...")
            shutdown_result = await client.call_tool("close_browser", {})
            logger.info("Shutdown result: %s", shutdown_result)

    except ConnectionRefusedError:
        logger.error(
            "Connection to MCP server at %s refused. " "Ensure the server is running.",
            SERVER_ADDRESS,
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error("An unexpected error occurred: %s", e, exc_info=True)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
