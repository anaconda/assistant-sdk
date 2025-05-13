# anaconda-assistant-conda

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
conda install -n base -c anaconda-cloud anaconda-assistant-conda
```

## Terms of use

You will need to agree to our terms of use, privacy policy, and choose to opt-in or opt-out of data collection
on first use of this plugin.

See the [documentation from the anaconda-assistant-sdk](https://github.com/anaconda/assistant-sdk/tree/main/libs/anaconda-assistant-sdk#terms-of-use-and-data-collection) for more details.

## Authentication

When you use any of the Anaconda AI Assistant features you will be prompted to login to your Anaconda.cloud
account if you have not already done so. This will open your browser and prompt you to complete the login.

You can also login using the Anaconda CLI

```text
anaconda login
```

## Daily quotas

Each Anaconda.cloud subscription plan enforces a limit on the number of requests.
The limits are documented on the [Plans and Pricing page](https://www.anaconda.com/pricing). Once the limit is reached the plugin will display a message to wait for 24 hours.

Users can upgrade their plans by visiting [https://anaconda.cloud/profile/subscriptions](https://anaconda.cloud/profile/subscriptions).

## Error messages

Conda command can fail in many ways and sometimes the error message doesn't immediately help you correct the problem.

When any conda CLI command produces an error message the Assistant will intercept the message and help you diagnose
the problem and suggest corrections.

```text
> conda create -n myenv --dry-run anaconda-cloud-auth=0.7 pydantic=1
Channels:
 - defaults
 - ai-staging
 - anaconda-cloud
 - conda-forge
Platform: osx-arm64
Collecting package metadata (repodata.json): done
Solving environment: failed

LibMambaUnsatisfiableError: Encountered problems while solving:
  - nothing provides package_has_been_revoked needed by anaconda-cli-base-0.4.1-py310hca03da5_0

Could not solve for environment specs
The following packages are incompatible
├─ anaconda-cloud-auth 0.7**  is installable and it requires
│  └─ anaconda-cli-base >=0.4.0  with the potential options
│     ├─ anaconda-cli-base 0.4.1 would require
│     │  └─ package_has_been_revoked, which does not exist (perhaps a missing channel);
│     └─ anaconda-cli-base [0.4.0|0.4.1] would require
│        └─ pydantic-settings >=2.3 , which requires
│           └─ pydantic >=2.7.0 , which can be installed;
└─ pydantic 1**  is not installable because it conflicts with any installable versions previously reported.

Hello from Anaconda Assistant!
I'm going to help you diagnose and correct this error.
The error message indicates that there are compatibility issues between the packages you are trying to install. Specifically,
the package anaconda-cloud-auth version 0.7 requires anaconda-cli-base version 0.4.0 or higher, but the available version
0.4.1 has a dependency on a package that has been revoked (package_has_been_revoked). Additionally, the version of pydantic
you specified (1) conflicts with the requirements of anaconda-cli-base, which needs a version of pydantic that is 2.7.0 or higher.

Here are three ways you can correct the error:

 1 Update the pydantic version: Change the command to specify a compatible version of pydantic that meets the requirements of
   anaconda-cli-base. For example:

    conda create -n myenv --dry-run anaconda-cloud-auth=0.7 pydantic=2.7.0

 2 Remove anaconda-cloud-auth: If you do not specifically need anaconda-cloud-auth, you can try creating the environment
   without it:

    conda create -n myenv --dry-run pydantic=2.7.0

 3 Use a different version of anaconda-cloud-auth: If you need anaconda-cloud-auth, consider using a different version that
   does not have the same dependency issues. You can check for available versions and try a lower version:

    conda create -n myenv --dry-run anaconda-cloud-auth=0.6 pydantic=2.7.0


Make sure to check the compatibility of the packages you choose to install.
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

### Run the unit tests

```shell
make test
```

### Run the unit tests across isolated environments with tox

NOTE: this may not run locally

```shell
make tox
```
