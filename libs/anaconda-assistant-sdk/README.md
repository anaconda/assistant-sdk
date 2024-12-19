# anaconda-assistant

The Anaconda Assistant Python client

## Installation

```text
conda install -c anaconda-cloud anaconda-assistant-sdk
```

## How to authenticate

To use the Python client or CLI you can use `anaconda login` CLI, Anaconda Navigator, or

```python
from anaconda_cloud_auth import login
login()
```

to launch a browser to login and save your API token to disk. For cases where you cannot utilize a browser to login you can grab your API and set the `ANACONDA_CLOUD_API_KEY=<api-key>` env var.

The Python clients and integrations provide `api_key` as a keyword argument.

## Terms of use and data collection

In order to use the Anaconda Assistant SDK and derived integrations the user must first agree to

* Our [terms of service](https://legal.anaconda.com/policies/en/?name=terms-of-service#anaconda-terms-of-service)
* Our [privacy policy](https://legal.anaconda.com/policies/en/?name=privacy-policy)
* Assert that they are more than 13 years old
* Opt-in or Opt-out of Data Collection

On Data Collection:
If you opt-in you will enjoy personalized recommendations and contribute to smarter features.

We prioritize your privacy:

* Your data is never sold
* Always secured
* This setting only affects the data Anaconda stores
* It does not affect the data that is sent to Open AI

To agree to the terms of service and configure data collection edit the `~/.anaconda/config.toml` file

```toml
[plugin.assistant]
accepted_terms = true
data_collection = true
```

You may set `data_collection = false` if you chose to opt-out.

If you set `accepted_terms = false` the Anaconda Assistant SDK and derived integrations will not function.

If either or both of these values are unset in the `~/.anaconda/config.toml` file, an exception will be raised.

## Chat session

The ChatSession provides a multi-turn chat interface that saves input and output messages. The response can be
streamed or provided in one chunk.

```python
from anaconda_assistant import ChatSession

chat = ChatSession()

text = chat.completions("what are the the first 5 fibonacci numbers?", stream=False)
print(text)

text = chat.completions("make that the first 10 numbers", stream=False)
print(text)
```

## Chat client

The ChatClient provides a low-level completions function that accepts a list of messages in the same format
as OpenAI. The `completions()` method returns a ChatResponse object that allows streaming of the response similar to
requests Response.

```python
from anaconda_assistant import ChatClient

client = ChatClient()

messages = [
    {"role": "user", "content": "What is pi?"}
]

response = chat.completions(messages=messages)

for chunk in response.iter_content():
    print(chunk, end="")
```

You can only consume the message with `.iter_content()` once, but the result is captured to the `.message` attribute
while streaming.

## Integrations

A number of 3rd party integrations are provided. In each case you will need to have optional packages installed.

### LLM CLI

The [LLM CLI](https://github.com/simonw/llm) can be use to send and receive messages with the Anaconda Assistant.

Required packages: `llm`

To direct your messages to Anaconda Assistant use the model name `anaconda-assistant`

```text
> llm -m anaconda-assistant 'what is pi?'
```

### LangChain

A [LangChain integration](https://python.langchain.com/docs/introduction/) is provided that supports message streaming and non-streaming responses.

Required packages: `langchain >=0.3`

```python
from anaconda_assistant.langchain import AnacondaAssistant
from langchain.prompts import ChatPromptTemplate

model = AnacondaAssistant()
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
chain = prompt | model

message = chain.invoke({'topic': 'python'})
print(message.content)
```

### ELL

You can use Anaconda Assistant as a model in the [ell](https://github.com/MadcowD/ell) prompt engineering framework.

Required packages: `ell-ai`

```python
import ell
import anaconda_assistant.integrations.ell

ell.init(verbose=True)

@ell.simple(model="anaconda-assistant")
def who():
    return "Who are you?"

who()
```

### PandasAI

To use Anaconda Assistant with [PandasAI](https://github.com/Sinaptik-AI/pandas-ai/tree/main) configure the SmartDataFrame using the AnacondaAssistant plugin

Required packages: `pandasai`

```python
from anaconda_assistant.pandasai import AnacondaAssistant
from pandasai import SmartDataframe

ai = AnacondaAssistant()
sdf = SmartDataframe(df, config={'llm': ai})
sdf.chat('what is the average of this column where some condition is true?')
```

### Panel

You can integrate the Anaconda Assistant in your Panel application using the [chat features](https://panel.holoviz.org/reference/index.html#chat) including the name and avatar for the signed in user.

Required packages: `panel`

```python
import panel as pn

from anaconda_assistant import ChatSession
from anaconda_assistant.integrations.panel import AnacondaAssistantCallbackHandler

assistant = ChatSession()
callback = AnacondaAssistantCallbackHandler(assistant)

chat = pn.chat.ChatInterface(
    callback=callback,
    user=assistant.auth_client.name,
    avatar=assistant.auth_client.avatar,
)
```

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
