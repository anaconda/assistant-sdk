# anaconda-assistant-mcp

## Overview

The Conda MCPServer provides a programmatic and natural language interface to manage conda environments, packages, and related operations. It is designed for integration with AI assistants (such as Cursor, Claude, and VSCode) to enable seamless, conversational control over conda workflows.

## Capabilities

The MCPServer exposes a set of core conda management features, accessible via API or natural language prompts (when integrated with an AI assistant):
- Create a new environment
- List all environments
- Show environment details
- Install, update, or remove packages
- Search for available packages
- Remove environments

### Example Natural Language Prompts
- **Create an environment:**
  - "Create a new conda environment named myenv with Python 3.10 and numpy."
- **List environments:**
  - "Show all my conda environments."
- **Show details:**
  - "What packages are installed in the myenv environment?"
- **Install or update packages:**
  - "Add pandas and matplotlib to myenv."
  - "Update numpy in myenv to the latest version."
- **Search for packages:**
  - "Find all available versions of scikit-learn."
- **Remove environment:**
  - "Delete the environment called oldenv."

## Installation

### Prerequisites
- Python 3.10 or newer
- Conda (Miniconda or Anaconda)

### Install with both channels (Recommended)

```bash
conda install -n base -c anaconda-cloud -c conda-forge anaconda-assistant-mcp
```

## Start the MCP server

```bash
conda mcp serve
```

## Configuration for AI Clients

To allow AI clients to connect to your MCPServer, you must create a configuration file with the correct name, location, and contents. Use the exact instructions below for your client.

### 1. Cursor
- **File name:** `mcp.json`
- **File location:** `~/.cursor/mcp.json`
- **File contents:**

```json
{
  "mcpServers": {
    "conda-mcp-dev": {
      "command": "/path/to/conda",
      "args": ["mcp", "serve"]
    }
  }
}
```
- The `command` field should point to the full path of your conda executable inside your MCP environment.
- The `args` array should contain the arguments to start the MCP server (typically `["mcp", "serve"]`).

**How to find your conda path:**

```bash
conda info --base
```
Then append the OS-specific path:
- **Unix/macOS/Linux:** `$(conda info --base)/bin/conda`
- **Windows:** `$(conda info --base)/Scripts/conda.exe` or `$(conda info --base)\Scripts\conda.exe`

**Common conda locations:**

**Anaconda installations:**
- **macOS:** `/opt/anaconda3/bin/conda` or `~/anaconda3/bin/conda`
- **Linux:** `~/anaconda3/bin/conda` or `/home/username/anaconda3/bin/conda`
- **Windows:** `C:\Users\username\Anaconda3\Scripts\conda.exe`

**Miniconda installations:**
- **macOS:** `/opt/miniconda3/bin/conda` or `~/miniconda3/bin/conda`
- **Linux:** `~/miniconda3/bin/conda`
- **Windows:** `C:\Users\username\Miniconda3\Scripts\conda.exe`

**How to create or edit the file:**
```bash
mkdir -p ~/.cursor
vim ~/.cursor/mcp.json
```
Paste the JSON above, save, and exit.

To see code changes reflected in Cursor, go to the top right gear icon ⚙️, select "Tools & Integrations" in the left menu, then toggle the name of the MCP server on. Every time you make changes to the code, toggle the server off and on again so the changes are picked up.

### 2. Claude Desktop
- **File name:** `claude_desktop_config.json`
- **File location:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **File contents:**

```json
{
  "mcpServers": {
    "conda-mcp-dev": {
      "command": "/path/to/conda",
      "args": ["mcp", "serve"]
    }
  }
}
```
- The `command` field should point to the full path of your conda executable inside your MCP environment.
- The `args` array should contain the arguments to start the MCP server (typically `["mcp", "serve"]`).

**How to edit:**
```bash
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json
```
Paste or update the JSON above, save, and exit.

To see if the server is running correctly, click the “Search and tools” button in the main Claude menu. If the server is running, you will see “conda-mcp-dev” as one of the options. Try typing “mcp list packages” to see if the server/tools are working as expected.

### 3. VSCode
- **File name:** `mcp.json`
- **File location:**
  - Global: `~/.vscode/mcp.json`
  - Project-specific: `<your-project-root>/mcp.json`
- **File contents:**

```json
{
  "mcpServers": {
    "conda-mcp-dev": {
      "command": "/path/to/conda",
      "args": ["mcp", "serve"]
    }
  }
}
```
- The `command` field should point to the full path of your conda executable inside your MCP environment.
- The `args` array should contain the arguments to start the MCP server (typically `["mcp", "serve"]`).

**How to create or edit the file:**
- For a global config:
  ```bash
  mkdir -p ~/.vscode
  vim ~/.vscode/mcp.json
  ```
- For a project config:
  ```bash
  vim <your-project-root>/mcp.json
  ```
Paste the JSON content above, save, and exit.

**How to use in VSCode:**
If you are using a VSCode extension that supports external tool integration (such as a code assistant or LLM plugin), open the extension’s settings and set the path to your mcp.json file, or paste the JSON contents into the appropriate configuration field. Restart VSCode after making changes to ensure the extension loads the new configuration.

### Summary Table

| Client   | File Path Example                                                    | Example JSON Content |
|----------|---------------------------------------------------------------------|---------------------|
| Cursor   | `~/.cursor/mcp.json`                                                | `{ "mcpServers": { "conda-mcp-dev": { "command": "...", "args": ["mcp", "serve"] } } }` |
| Claude   | `~/Library/Application Support/Claude/claude_desktop_config.json`   | `{ "mcpServers": { "conda-mcp-dev": { "command": "...", "args": ["mcp", "serve"] } } }` |
| VSCode   | `~/.vscode/mcp.json` or `<your-project-root>/mcp.json`              | `{ "mcpServers": { "conda-mcp-dev": { "command": "...", "args": ["mcp", "serve"] } } }` |

## Using MCPServer Capabilities

After setup, you can use natural language prompts to trigger conda operations via your AI assistant. See the "Capabilities" section above for examples.

## Integration Steps
1. Start the MCPServer (locally or remotely)
2. Create the configuration file as described above for your client
3. Restart your client (Cursor, Claude, etc.) to ensure it loads the new configuration
4. Use natural language prompts to trigger conda operations

## Troubleshooting & Tips
- **Triggering the MCPServer:** Use clear, explicit prompts mentioning “conda”, “environment”, or “package” to help the AI recognize the request is for the MCPServer.
- **Environment Not Found:** Double-check the environment name; use “list environments” to see available ones.
- **Package Not Found:** Specify the correct package name; use “search for [package]” to verify availability.
- **Permissions Issues:** Ensure the MCPServer process has the necessary permissions to manage environments.
- **Server Connection Issues:** Verify the MCPServer is running and accessible at the configured endpoint in your config file.
- **Location of config file:** Place the config file in the exact path required by your client, and make sure the client is pointed to the correct path.
- **Multiple Clients:** You can use the same config file for all clients, as long as they support it.
- **Testing:** After setup, try a simple prompt like “List all conda environments” to verify the connection.

## Additional Resources
- [Conda Documentation](https://docs.conda.io/)

**Tip:** When using an AI assistant, you can often prefix your prompt with “In conda,” or “Using the conda server,” to ensure the request is routed to the MCPServer.

---

## Setup for development

Ensure you have `conda` installed.
Then run:

```shell
make setup
```

To run test commands, you don't want to run `conda mcp serve` since it'll pick up the version of conda on your system. You want the conda install for this repo so you can run the plugin. To do this, you run:

```shell
cd libs/anaconda-assistant-mcp
./env/bin/conda mcp serve
```

On Windows, you'll do:

```shell
.\env\Scripts\conda mcp serve
```

This will run the MCP server. Use it for sanity checking. To actually test fully, you'll want to add them MCP server into Claude Desktop or Cursor.

#### Cursor

The MCP config file is in your home directory at:

```
~/.cursor/mcp.json
```

Add this to your JSON under `mcpServers`:

```json
{
  "mcpServers": {
    "conda-mcp-dev": {
      "command": "<PATH_TO_SDK_REPO>/libs/anaconda-assistant-mcp/env/bin/conda",
      "args": ["mcp", "serve"]
    }
  }
}
```

To see code changes reflected in Cursor, go to the top right gear icon ⚙️ and click it, select "Tools & Integrations" in the left menu, then toggle the name of the MCP server on. In our case, that's "conda-mcp-dev", but it can be any string you choose. Every time you make changes to the code, you should toggle the sever off and on again so the changes are picked up.

Now, to test a feature. Open a new chat, remove all the context and type "mcp list packages". This should prompt you with the `list_packages` MCP tool. Press ⌘⏎ to run the tool.

#### Claude Desktop

Claude settings are the same, just under a different directory:

```
'~/Library/Application Support/Claude/claude_desktop_config.json'
```

```json
{
  "mcpServers": {
    "conda-mcp-dev": {
      "command": "<PATH_TO_SDK_REPO>/libs/anaconda-assistant-mcp/env/bin/conda",
      "args": ["mcp", "serve"]
    }
  }
}
```

Seeting changes reflected in Claude is more difficult than in Cursor. The most reliable way is to restart the Claude Desktop app.

Try using it by typing "mcp list packages". You should see it prompt you. After accepting, it should run the tool.

#### Notes

the name `conda-mcp-dev` can be any string. The purpose of it is to help you identify the MCP in the respective MCP host's UI whether it be Claude or Cursor.

Make sure to not enable MCP servers / tools with overlapping goals. Sometimes your MCP server won't get called because another MCP server will pick up the request.

### Run the unit tests

```shell
make test
```

### Run the unit tests across isolated environments with tox

NOTE: this may not run locally

```shell
make tox
```
