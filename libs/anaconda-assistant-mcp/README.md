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
./env/bin/conda assist ...
```

On Windows, you'll do:

```shell
.\env\Scripts\conda assist ...
```

### Run the unit tests

```shell
make test
```

### Run the unit tests across isolated environments with tox

NOTE: this may not run locally

```shell
make tox
```
