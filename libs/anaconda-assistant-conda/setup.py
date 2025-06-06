from setuptools import setup, find_packages

setup(
    name="anaconda-assistant-conda",
    version="0.1.0",
    description="The Anaconda Assistant conda plugin",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "anaconda-cli-base >=0.5",
        "anaconda-assistant-sdk >=0.4",
        "anaconda-auth >=0.8",
        "rich",
        "requests",
        "pydantic >=2",
        "tomli",
        "tomli-w",
        "typer[all]>=0.9.0",
        "pydantic-settings",
        "keyring",
        "pyyaml",
        "jsonschema"
    ],
    entry_points={
        "console_scripts": [
            "mcp=anaconda_assistant_conda.mcp.cli:main",
        ],
        "conda": [
            "anaconda-assistant=anaconda_assistant_conda.plugin",
            "mcp=anaconda_assistant_conda.mcp.cli:main",
        ],
    },
)