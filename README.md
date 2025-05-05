# Anaconda Assistant SDK and integrations

Here you will find the SDK for the Anaconda Assistant API the powers the [Anaconda Assistant
Jupyter Notebook extension](https://docs.anaconda.com/anaconda-notebooks/anaconda-assistant/).
Additional plugin or integration packages are also in this repo.

## Packages

* [anaconda-assistant-sdk](https://github.com/anaconda/assistant-sdk/tree/main/libs/anaconda-assistant-sdk)
    * This is the main Python SDK that provides clients for the API to send messages and receive replies.
    * Included here are integrations for many AI toolkit libraries, like [langchain](https://github.com/langchain-ai/langchain), [llm](https://github.com/simonw/llm), [ell](https://github.com/MadcowD/ell), and [Panel ChatInterface](https://panel.holoviz.org/reference/chat/ChatInterface.html).
    * See the [README](https://github.com/anaconda/assistant-sdk/blob/main/libs/anaconda-assistant-sdk/README.md) for more details
* [anaconda-assistant-conda](https://github.com/anaconda/assistant-sdk/tree/main/libs/anaconda-assistant-conda)
    * A [conda](https://github.com/conda/conda) plugin that provides AI assistance to conda workflows.
    * Error summarization and suggestions for corrections for all conda commands.
