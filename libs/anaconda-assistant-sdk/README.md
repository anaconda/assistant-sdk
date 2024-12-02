# anaconda-assistant

The Anaconda Assistant Python client

## How to authenticate

To use the Python client or CLI you can use `anaconda login` CLI, Anaconda Navigator, or

```python
from anaconda_cloud_auth import login
login()
```

 to launch a browser to login and save your API token to disk. For cases where you cannot utilize a browser to login you can grab your API and set the `ANACONDA_CLOUD_API_KEY=<api-key>` env var.

When using the Python client you may also set the api key when making a ChatSession object `ChatSession(api_key=...)`.

## Python client

```python
from anaconda_assistant import ChatSession

chat = ChatSession()

text = chat.completions("what are the the first 5 fibonacci numbers?", stream=False)
print(text)

text  = chat.completions("make that the first 10 numbers", stream=False)
print(text)
```

## CLI commands

```
❯ anaconda assistant

 Usage: anaconda assistant [OPTIONS] COMMAND [ARGS]...

 The Anaconda Assistant

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ conda                 Discover and install conda packages                                                                          │
│ debug                 Run a Python script and explain the error                                                                    │
│ snippet               Generate a Python snippet                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Panel integration

See the [panel-chat.py](https://github.com/anaconda/anaconda-cloud-tools/blob/2d731211eabe9994bc5167483bf1db2923e64d41/libs/anaconda-assistant/tests/panel-chat.py) file for how to utilize the chat callback.

To use the Panel auth provider you will need your own Anaconda.cloud auth client with ID and secret. To invoke the auth plugin for the panel-chat.py file above

```
PANEL_OAUTH_KEY=<key> PANEL_OAUTH_SECRET=<secret> PANEL_COOKIE_SECRET=<cookie-name> panel serve --oauth-provider anaconda_cloud --oauth-optional panel-chat.py --show
```

You can use the `ANACONDA_CLOUD_AUTH_DOMAIN` env var to change the default value of `id.anaconda.cloud`


## Setup for development

Ensure you have `conda` installed.
Then run:
```shell
make setup
```

## Run the unit tests
```shell
make test
```

## Run the unit tests across isolated environments with tox
```shell
make tox
```
