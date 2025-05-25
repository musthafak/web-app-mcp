# Python MCP Server for Web Automation

## Overview

This project provides a Multi-Capability Provider (MCP) server designed to assist Large Language Models (LLMs) and other programmatic clients in performing web automation tasks. It leverages the Playwright library to control web browsers and expose a simplified tool-based API for common web interactions.

## Features

*   **Browser Management**: Launch and close browsers (Chromium, Firefox, WebKit).
*   **Page Navigation**: Open URLs and manage browser pages.
*   **Element Interaction**: Click, fill input fields, retrieve attributes, and get text content of web elements.
*   **Element Discovery**: Capture details of multiple elements based on selectors and wait for elements to appear.
*   **JavaScript Evaluation**: Execute JavaScript within the context of a specific element.
*   **Screenshotting**: Capture screenshots of web pages.
*   **Extensible**: Built with FastMCP, allowing for easy addition of new tools.

## Prerequisites

*   Python (3.8+ recommended)
*   Pip (Python package installer)
*   Access to a terminal or command line interface.

## Installation

1.  **Clone the repository (if applicable)**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies**:
    This will install `fastmcp`, `playwright`, and other necessary Python packages.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers**:
    This command installs the necessary browser binaries (e.g., Chromium, Firefox, WebKit) along with their dependencies.
    ```bash
    playwright install --with-deps
    ```
    Alternatively, to install only a specific browser (e.g., Chromium):
    ```bash
    playwright install --with-deps chromium
    ```

## Running the Server

To start the MCP server:

```bash
python mcp_server/main.py
```

By default, the server will start on `localhost:8765`. You should see logging output indicating the server is running.

## Available Tools (API)

The server exposes the following tools that can be called by an MCP client (like the one in `example.py`):

---

### Browser Tools

1.  **`launch_browser`**
    *   **Description**: Launches the specified browser (Chromium, Firefox, or WebKit) and creates a new browser context. Initializes Playwright if not already started.
    *   **Parameters**:
        *   `browser_name: str` (optional, default: `'chromium'`). Options: `'chromium'`, `'firefox'`, `'webkit'`.
        *   `headless: bool` (optional, default: `True`). Whether to run the browser in headless mode.
    *   **Client Example**:
        ```python
        await client.execute_tool("launch_browser", {"browser_name": "firefox", "headless": False})
        ```

2.  **`close_browser`**
    *   **Description**: Closes the currently active browser, including all its pages and contexts. Also stops the Playwright instance.
    *   **Parameters**: None.
    *   **Client Example**:
        ```python
        await client.execute_tool("close_browser", {})
        ```

3.  **`new_page`**
    *   **Description**: Creates a new page in the current browser context. If an old page exists, it will be closed first.
    *   **Parameters**: None.
    *   **Client Example**:
        ```python
        await client.execute_tool("new_page", {})
        ```

---

### Page Tools

1.  **`goto_page`**
    *   **Description**: Navigates the current page to the specified URL.
    *   **Parameters**:
        *   `url: str` (required). The URL to navigate to (e.g., `"https://www.example.com"`).
    *   **Client Example**:
        ```python
        await client.execute_tool("goto_page", {"url": "https://playwright.dev"})
        ```

2.  **`capture_screenshot`**
    *   **Description**: Captures a screenshot of the current page and returns it as a base64 encoded string.
    *   **Parameters**: None.
    *   **Client Example**:
        ```python
        base64_image = await client.execute_tool("capture_screenshot", {})
        # To save the image, you would decode it and write to a file:
        # import base64
        # image_data = base64.b64decode(base64_image)
        # with open("screenshot.png", "wb") as f:
        #     f.write(image_data)
        ```

3.  **`get_current_url`**
    *   **Description**: Gets the current URL of the active page.
    *   **Parameters**: None.
    *   **Client Example**:
        ```python
        current_url = await client.execute_tool("get_current_url", {})
        print(f"The current URL is: {current_url}")
        ```

4.  **`get_page_title`**
    *   **Description**: Gets the title of the current active page.
    *   **Parameters**: None.
    *   **Client Example**:
        ```python
        page_title = await client.execute_tool("get_page_title", {})
        print(f"The page title is: {page_title}")
        ```

5.  **`capture_area_snapshot`**
    *   **Description**: Captures the W3C Accessibility Object Model (AOM) representation of the current page or a specific element's subtree. The AOM is a structured dictionary that can be large and complex.
    *   **Parameters**:
        *   `selector: str` (optional, default: `None`). The CSS selector for the root element of the accessibility tree snapshot. If `None` or an empty string, the snapshot is taken for the entire page.
    *   **Returns**: A dictionary representing the AOM, or an error message string.
    *   **Client Example**:
        ```python
        # Capture AOM for the entire page
        page_aom = await client.execute_tool("capture_area_snapshot", {})
        
        # Capture AOM for a specific element (e.g., the main content area)
        element_aom = await client.execute_tool("capture_area_snapshot", {"selector": "main#content"})
        
        if isinstance(element_aom, dict):
            print(f"Role of the element: {element_aom.get('role')}")
        else:
            print(element_aom) # Error message
        ```

6.  **`wait_for_navigation`**
    *   **Description**: Waits for the page to navigate to a new URL or for a specific load state to be reached. This is typically used after an action that triggers navigation (e.g., clicking a link or submitting a form).
    *   **Parameters**:
        *   `url: str` (optional, default: `None`). A glob pattern, regex pattern (e.g., `"/articles/.*"`), or full URL to match the target URL. If `None`, waits for the next navigation to any URL.
        *   `wait_until: str` (optional, default: `None`). The load state to wait for. Common values: `'load'` (default if not specified), `'domcontentloaded'`, `'networkidle'` (waits until no network connections for 500ms), `'commit'`.
        *   `timeout: float` (optional, default: `None`). Maximum time to wait for navigation in seconds. If `None`, Playwright's default (typically 30 seconds) is used.
    *   **Returns**: A success message like "Navigation completed. Final URL: [URL]" or an error message if timeout or other issues occur.
    *   **Client Example**:
        ```python
        # After clicking a link that should go to an article page:
        # await client.execute_tool("click_element", {"selector": "a.article-link"})
        
        # Wait for navigation to any URL, using default load state and timeout
        # status = await client.execute_tool("wait_for_navigation", {})
        
        # Wait for navigation to a URL matching a regex, until DOM is loaded, with 10s timeout
        status = await client.execute_tool(
            "wait_for_navigation",
            {
                "url": "**/articles/.*",
                "wait_until": "domcontentloaded",
                "timeout": 10.0
            }
        )
        print(status)
        ```

7.  **`close_page`**
    *   **Description**: Closes the current active page.
    *   **Parameters**: None.
    *   **Client Example**:
        ```python
        await client.execute_tool("close_page", {})
        ```

---

### Element Interaction Tools

1.  **`click_element`**
    *   **Description**: Clicks the element specified by the CSS selector.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element to click (e.g., `"#submit-button"`).
    *   **Client Example**:
        ```python
        await client.execute_tool("click_element", {"selector": "button.primary"})
        ```

2.  **`hover_element`**
    *   **Description**: Hovers the mouse cursor over the element specified by the CSS selector. This can trigger actions like dropdown menus or tooltips.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element to hover over.
    *   **Client Example**:
        ```python
        await client.execute_tool("hover_element", {"selector": "nav #user-menu"})
        ```

3.  **`fill_element`**
    *   **Description**: Fills an input field (specified by selector) with the provided text.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the input element.
        *   `text: str` (required). The text to fill into the input field.
    *   **Client Example**:
        ```python
        await client.execute_tool("fill_element", {"selector": "input[name='username']", "text": "john.doe"})
        ```

3.  **`capture_elements`**
    *   **Description**: Finds all elements matching the CSS selector and captures their details (innerText, innerHTML, attributes).
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the elements.
    *   **Client Example**:
        ```python
        elements_data = await client.execute_tool("capture_elements", {"selector": "div.product-item"})
        # elements_data will be a list of dictionaries
        ```

5.  **`evaluate_element`**
    *   **Description**: Finds the first element matching the selector and evaluates a JavaScript expression in its context.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
        *   `expression: str` (required). The JavaScript expression to evaluate (e.g., `"element => element.value"` or `"element => getComputedStyle(element).backgroundColor"`).
    *   **Client Example**:
        ```python
        value = await client.execute_tool("evaluate_element", {"selector": "#myInput", "expression": "el => el.value"})
        ```

5.  **`get_element_html`**
    *   **Description**: Gets the `outerHTML` of the first element matching the selector, with options to clean and truncate the HTML.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
        *   `char_limit: int` (optional, default: `None`). If set, truncates the HTML to this character limit.
        *   `remove_scripts: bool` (optional, default: `False`). If `True`, removes `<script>` tags.
        *   `remove_comments: bool` (optional, default: `False`). If `True`, removes HTML comments.
        *   `remove_styles: bool` (optional, default: `False`). If `True`, removes `<style>` and `<link rel="stylesheet">` tags.
    *   **Client Example**:
        ```python
        # Get full HTML for an element
        html_content = await client.execute_tool("get_element_html", {"selector": "div.article-content"})
        
        # Get HTML, remove scripts and styles, and truncate to 500 chars
        cleaned_html = await client.execute_tool(
            "get_element_html",
            {
                "selector": "main#content",
                "char_limit": 500,
                "remove_scripts": True,
                "remove_styles": True
            }
        )
        ```

7.  **`get_element_attribute`**
    *   **Description**: Gets the value of a specified attribute for the first element matching the selector.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
        *   `attribute_name: str` (required). The name of the attribute to get (e.g., `"href"`, `"data-id"`).
    *   **Client Example**:
        ```python
        link_href = await client.execute_tool("get_element_attribute", {"selector": "a.mylink", "attribute_name": "href"})
        ```

8.  **`get_element_bounding_box`**
    *   **Description**: Gets the bounding box (x, y, width, height) of the first element matching the selector.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
    *   **Returns**: A dictionary like `{'x': float, 'y': float, 'width': float, 'height': float}` or an error message.
    *   **Client Example**:
        ```python
        bounding_box = await client.execute_tool("get_element_bounding_box", {"selector": "img#main-logo"})
        if isinstance(bounding_box, dict):
            print(f"Logo position: x={bounding_box['x']}, y={bounding_box['y']}")
        else:
            print(bounding_box) # Error message
        ```

9.  **`get_text_content`**
    *   **Description**: Gets the `textContent` of the first element matching the selector.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
    *   **Client Example**:
        ```python
        text = await client.execute_tool("get_text_content", {"selector": "h1"})
        ```

10. **`wait_for_selector`**
    *   **Description**: Waits for an element matching the CSS selector to appear on the page within a specified timeout.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector to wait for.
        *   `timeout: int` (optional, default: `30000` milliseconds). Maximum time to wait.
    *   **Client Example**:
        ```python
        await client.execute_tool("wait_for_selector", {"selector": "#dynamic-content", "timeout": 10000})
        ```

---

## Example Client Usage

An example client script, `example.py`, is provided in the root of this project. It demonstrates how to connect to the MCP server and use some of the available tools.

1.  **Ensure the MCP server is running**:
    ```bash
    python mcp_server/main.py
    ```

2.  **In a separate terminal, run the example client**:
    ```bash
    python example.py
    ```
    The client will connect to the server, launch a browser, navigate to `example.com`, extract the heading text, take a screenshot (which can be saved as `example_screenshot.png`), and then close everything down.

## Running Tests

Unit tests are provided to ensure the tools function correctly.

1.  **Install test dependencies** (if not already installed via `requirements.txt`):
    ```bash
    pip install pytest
    ```
    (Note: `pytest` is usually included as a development dependency. If your `requirements.txt` is for production only, you might need to install it separately or from a `requirements-dev.txt`.)

2.  **Run tests**:
    Execute `pytest` from the project's root directory:
    ```bash
    pytest
    ```
    This will discover and run all tests in the `tests/` directory.

## Contributing

Contributions are welcome! If you find any bugs, have feature requests, or want to improve the project:

1.  **Report Issues**: Please open an issue on the project's issue tracker, detailing the bug or enhancement.
2.  **Submit Pull Requests**:
    *   Fork the repository.
    *   Create a new branch for your feature or fix.
    *   Make your changes, including adding relevant tests.
    *   Ensure all tests pass.
    *   Submit a pull request with a clear description of your changes.

---
This README provides a comprehensive guide to understanding, installing, and using the Python MCP Server.
