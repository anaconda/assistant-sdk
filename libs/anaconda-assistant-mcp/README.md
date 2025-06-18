# anaconda-assistant-mcp

The Anaconda AI Assistant conda plugin brings AI assistance to your conda workflows.
You will need an account on Anaconda.cloud. Visit the [sign-up](https://anaconda.cloud/sign-up) page
to create an account.

Refer to [https://anaconda.com/pricing](https://www.anaconda.com/pricing) for information about the
number of Anaconda AI Assistant requests you can make.

The plugin provides a new subcommand called `conda assist` and will automatically summarize error messages
for all conda commands and provide suggestions on how to correct the error.

## Installation

This package is a [conda plugin](https://docs.conda.io/projects/conda/en/latest/dev-guide/plugins/index.html) and must be installed in your `base` environment.
Conda version 24.1 or newer is required.

```text
conda install -n base -c anaconda-cloud anaconda-assistant-mcp
```

## Setup for development

Ensure you have `conda` installed.
Then run:

```shell
make setup
```

To run test commands, you don't want to run `conda assist` since it'll pick up the version of conda on your system. You want the conda install for this repo so you can run the plugin. To do this, you run:

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

### Run the unit tests

```shell
make test
```

### Run the unit tests across isolated environments with tox

NOTE: this may not run locally

```shell
make tox
```
