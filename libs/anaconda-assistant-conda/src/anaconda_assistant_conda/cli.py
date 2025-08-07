import sys
import re
from typing import Dict, Any, Optional, List, Union

import typer
from rich.console import Console
from typing_extensions import Annotated

import asyncio
from fastmcp import Client

from .prompt_debug_config import prompt_debug_config
from .config import AssistantCondaConfig

console = Console()

helptext = """
The conda assistant, powered by Anaconda Assistant. \n
See https://anaconda.com/docs/tools/working-with-conda/cli-assistant for more information.

Examples:
  conda assist chat "create a conda environment with python 3.8 and numpy"
  conda assist chat "list all my conda environments"
  conda assist chat "show details for environment myenv"
  conda assist chat "add pandas to myenv"
  conda assist chat "remove environment oldenv"
"""

app = typer.Typer(
    help=helptext,
    add_help_option=True,
    no_args_is_help=True,
    add_completion=False,
)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def _(prompt: Annotated[Optional[str], typer.Argument(help="Natural language description of the conda operation to perform")] = None) -> None:
    """Main entry point for conda assist."""
    if prompt:
        # If a prompt is provided directly, treat it as a chat command
        chat(prompt)
    # If no prompt, show help (default behavior)


@app.command(name="config")
def config() -> None:
    prompt_debug_config()


@app.command(name="configure")
def configure() -> None:
    console.print(
        "[yellow]Warning: The 'configure' command is deprecated and will be removed in a future version. Please use `conda assist config`.[/yellow]"
    )
    prompt_debug_config()


@app.command(name="mcp")
def mcp(prompt: str) -> None:
    """Send a prompt to an already-running MCP server and print the response."""
    async def run() -> None:
        async with Client(transport="stdio") as client:
            # Call the list_environment tool as a test
            try:
                result = await client.call_tool("list_environment", {})
                print(result[0].text if result else "No response from server.")
            except Exception as e:
                print(f"Error communicating with MCP server: {e}")
    asyncio.run(run())


def parse_natural_language_prompt(prompt: str) -> Dict[str, Any]:
    """
    Parse natural language prompt and map to MCP tool parameters.
    
    Returns a dictionary with:
    - tool_name: The MCP tool to call
    - parameters: Dict of parameters for the tool
    """
    prompt_lower = prompt.lower().strip()
    
    # Create environment patterns - order matters!
    create_patterns = [
        # "create environment with packages" (most common)
        r"create\s+(?:a\s+)?(?:conda\s+)?environment\s+with\s+(.+)",
        # "create environment named myenv with packages"
        r"create\s+(?:a\s+)?(?:conda\s+)?environment\s+(?:named\s+)?(\w+)(?:\s+with\s+(.+))?",
        # "create environment with packages named myenv"
        r"create\s+(?:a\s+)?(?:conda\s+)?environment\s+with\s+(.+?)(?:\s+named\s+(\w+))?",
        # "new environment named myenv with packages"
        r"new\s+(?:conda\s+)?environment\s+(?:named\s+)?(\w+)(?:\s+with\s+(.+))?",
    ]
    
    for i, pattern in enumerate(create_patterns):
        match = re.search(pattern, prompt_lower)
        if match:
            # Handle different pattern groups
            if len(match.groups()) == 2:
                if match.group(1) and match.group(2):
                    # Pattern: "create environment named myenv with packages"
                    env_name = match.group(1)
                    packages_spec = match.group(2)
                elif match.group(1) and not match.group(2):
                    # Pattern: "create environment with packages named myenv"
                    packages_spec = match.group(1)
                    env_name = "myenv"  # Default name
                else:
                    # Pattern: "create environment with packages"
                    packages_spec = match.group(1)
                    env_name = "myenv"  # Default name
            else:
                # Single group pattern
                packages_spec = match.group(1)
                env_name = "myenv"  # Default name
            
            # Extract Python version
            python_version = None
            py_match = re.search(r"python\s+(\d+\.\d+)", packages_spec)
            if py_match:
                python_version = py_match.group(1)
                # Remove python version from packages_spec
                packages_spec = re.sub(r"python\s+\d+\.\d+", "", packages_spec)
            
            # Extract packages
            packages = []
            if packages_spec.strip():
                # First split by commas, then by "and"
                package_list = []
                for part in packages_spec.split(','):
                    package_list.extend(part.split(' and '))
                
                packages = [pkg.strip() for pkg in package_list if pkg.strip() and pkg.strip() != "with" and pkg.strip() != "and"]
                # Filter out any packages that are just partial words
                packages = [pkg for pkg in packages if len(pkg) > 1 and not pkg.endswith(',')]
            
            return {
                "tool_name": "create_environment",
                "parameters": {
                    "env_name": env_name,
                    "python_version": python_version,
                    "packages": packages if packages else None
                }
            }
    
    # List environments patterns
    list_patterns = [
        r"list\s+(?:all\s+)?(?:my\s+)?(?:conda\s+)?environments?",
        r"show\s+(?:all\s+)?(?:my\s+)?(?:conda\s+)?environments?",
        r"what\s+(?:are\s+)?(?:my\s+)?(?:conda\s+)?environments?",
    ]
    
    for pattern in list_patterns:
        if re.search(pattern, prompt_lower):
            return {
                "tool_name": "list_environment",
                "parameters": {}
            }
    
    # Show environment details patterns
    details_patterns = [
        r"show\s+details?\s+(?:for\s+)?(?:environment\s+)?(\w+)",
        r"what\s+(?:packages?\s+)?(?:are\s+)?(?:installed\s+)?(?:in\s+)?(?:environment\s+)?(\w+)",
        r"details?\s+(?:for\s+)?(?:environment\s+)?(\w+)",
    ]
    
    for pattern in details_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            env_name = match.group(1)
            return {
                "tool_name": "show_environment_details",
                "parameters": {"env_name": env_name}
            }
    
    # Update environment patterns
    update_patterns = [
        r"(?:add|install)\s+(.+?)\s+(?:to|in)\s+(?:environment\s+)?(\w+)",
        r"update\s+(.+?)\s+(?:in|to)\s+(?:environment\s+)?(\w+)",
    ]
    
    for pattern in update_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            packages_spec = match.group(1)
            env_name = match.group(2)
            
            # Extract packages
            packages = []
            if packages_spec.strip():
                package_list = re.split(r"\s+(?:and|,)\s+", packages_spec.strip())
                packages = [pkg.strip() for pkg in package_list if pkg.strip()]
            
            return {
                "tool_name": "update_environment",
                "parameters": {
                    "packages": packages,
                    "env_name": env_name
                }
            }
    
    # Remove environment patterns
    remove_patterns = [
        r"(?:remove|delete)\s+(?:environment\s+)?(?:called\s+)?(\w+)",
        r"delete\s+(?:the\s+)?(?:environment\s+)?(?:called\s+)?(\w+)",
    ]
    
    for pattern in remove_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            env_name = match.group(1)
            return {
                "tool_name": "remove_environment",
                "parameters": {"name": env_name}
            }
    
    # Search packages patterns
    search_patterns = [
        r"search\s+(?:for\s+)?(.+?)(?:\s+packages?)?$",
        r"find\s+(?:all\s+)?(?:available\s+)?(?:versions?\s+)?(?:of\s+)?(.+)$",
    ]
    
    for pattern in search_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            package_name = match.group(1).strip()
            return {
                "tool_name": "search_packages",
                "parameters": {"package_name": package_name}
            }
    
    # If no pattern matches, return None
    return None


async def execute_mcp_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Execute an MCP tool with the given parameters."""
    try:
        async with Client(transport="stdio") as client:
            result = await client.call_tool(tool_name, parameters)
            if result and len(result) > 0:
                return result[0].text
            else:
                return "No response from MCP server."
    except Exception as e:
        return f"Error executing MCP tool '{tool_name}': {e}"


@app.command(name="chat")
def chat(prompt: Annotated[str, typer.Argument(help="Natural language description of the conda operation to perform")]) -> None:
    """Process natural language conda requests and execute them via MCP tools."""
    
    # Parse the natural language prompt
    parsed = parse_natural_language_prompt(prompt)
    
    if parsed is None:
        console.print(f"[red]Sorry, I couldn't understand your request: '{prompt}'[/red]")
        console.print("\n[bold]Supported operations:[/bold]")
        console.print("• Create environments: 'create a conda environment with python 3.8 and numpy'")
        console.print("• List environments: 'list all my conda environments'")
        console.print("• Show details: 'show details for environment myenv'")
        console.print("• Update environments: 'add pandas to myenv'")
        console.print("• Remove environments: 'remove environment oldenv'")
        console.print("• Search packages: 'search for scikit-learn'")
        return
    
    # Execute the MCP tool
    console.print(f"[bold]Executing: {parsed['tool_name']}[/bold]")
    console.print(f"[dim]Parameters: {parsed['parameters']}[/dim]\n")
    
    result = asyncio.run(execute_mcp_tool(parsed['tool_name'], parsed['parameters']))
    console.print(result)
