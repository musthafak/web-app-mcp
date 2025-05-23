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
    *   **Description**: Captures a screenshot of the current page and saves it to the specified path.
    *   **Parameters**:
        *   `path: str` (required). The file path where the screenshot will be saved (e.g., `"./screenshot.png"`).
    *   **Client Example**:
        ```python
        await client.execute_tool("capture_screenshot", {"path": "page_image.png"})
        ```

3.  **`close_page`**
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

2.  **`fill_element`**
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

4.  **`evaluate_element`**
    *   **Description**: Finds the first element matching the selector and evaluates a JavaScript expression in its context.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
        *   `expression: str` (required). The JavaScript expression to evaluate (e.g., `"element => element.value"` or `"element => getComputedStyle(element).backgroundColor"`).
    *   **Client Example**:
        ```python
        value = await client.execute_tool("evaluate_element", {"selector": "#myInput", "expression": "el => el.value"})
        ```

5.  **`get_element_attribute`**
    *   **Description**: Gets the value of a specified attribute for the first element matching the selector.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
        *   `attribute_name: str` (required). The name of the attribute to get (e.g., `"href"`, `"data-id"`).
    *   **Client Example**:
        ```python
        link_href = await client.execute_tool("get_element_attribute", {"selector": "a.mylink", "attribute_name": "href"})
        ```

6.  **`get_text_content`**
    *   **Description**: Gets the `textContent` of the first element matching the selector.
    *   **Parameters**:
        *   `selector: str` (required). The CSS selector for the element.
    *   **Client Example**:
        ```python
        text = await client.execute_tool("get_text_content", {"selector": "h1"})
        ```

7.  **`wait_for_selector`**
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
    The client will connect to the server, launch a browser, navigate to `example.com`, extract the heading text, take a screenshot (`example_screenshot.png`), and then close everything down.

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
