"""
MCP CLI module - Integrates rewritten MCP Manager functionality.
"""
import typer
import os
import sys # Added import
import subprocess # Added import
import shutil # Added import
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Import the new service and exceptions
from anaconda_assistant_conda.mcp.core.service import MCPManagerService
from anaconda_assistant_conda.mcp.core.exceptions import (
    MCPManagerError,
    ServerNotFoundError,
    ServerAlreadyInstalledError,
    ServerNotInstalledError,
    EnvironmentCreationError,
    EnvironmentRemovalError,
    PackageInstallationError,
    PackageUpdateError,
    ConfigurationError,
    ClientNotSupportedError
)

console = Console()

# Create a standalone Typer app for MCP commands
app = typer.Typer(
    help="Model Context Protocol (MCP) server management (Integrated)",
    add_help_option=True,
    no_args_is_help=True,
)

# Create server subcommand group
server_app = typer.Typer(
    help="MCP server operations",
    add_help_option=True,
    no_args_is_help=True,
)

# Add server subcommand group to mcp app
app.add_typer(server_app, name="server")

# Initialize MCP service
# Use a function to potentially allow for easier testing/mocking later
def get_mcp_service() -> MCPManagerService:
    return MCPManagerService()

# --- Commands --- #

@app.command("list", help="List all available MCP servers (shortcut for 'server list').")
def list_servers_shortcut() -> None:
    """Lists MCP servers available in the catalog."""
    service = get_mcp_service()
    try:
        servers = service.list_available_servers()

        if not servers:
            console.print("[yellow]No MCP servers found in the catalog.[/yellow]")
            return

        table = Table(title="Available MCP Servers")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        table.add_column("Description", style="green")

        for server in servers:
            table.add_row(server["name"], server.get("version", "N/A"), server.get("description", ""))

        console.print(table)

    except MCPManagerError as e:
        console.print(f"[bold red]Error listing servers:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)

@server_app.command("list", help="List all available MCP servers.")
def list_servers_cmd() -> None:
    """Alias for the top-level list command."""
    list_servers_shortcut()

@server_app.command("info", help="Show details about a specific server.")
def server_info(
    server_name: str = typer.Argument(..., help="The name of the MCP server to get information about.")
) -> None:
    """Shows detailed information about a specific MCP server from the catalog."""
    service = get_mcp_service()
    try:
        details = service.get_server_info(server_name)

        panel_content = Text()
        panel_content.append(f"Name: ", style="bold cyan")
        panel_content.append(f"{server_name}\n")
        panel_content.append(f"Package Name: ", style="bold magenta")
        panel_content.append(f"{details.get('package_name', 'N/A')}\n")
        panel_content.append(f"Version: ", style="bold yellow")
        panel_content.append(f"{details.get('version', 'N/A')}\n")
        panel_content.append(f"Description: ", style="bold green")
        panel_content.append(f"{details.get('description', 'No description available.')}\n")
        panel_content.append(f"Source: ", style="bold blue")
        panel_content.append(f"{details.get('source', 'N/A')}")

        console.print(Panel(panel_content, title=f"Server Info: {server_name}", border_style="blue"))

    except ServerNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except MCPManagerError as e:
        console.print(f"[bold red]Error getting server info:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)

@server_app.command("install", help="Install a server (globally or in workspace).")
def install_server(
    server_name: str = typer.Argument(..., help="The name of the MCP server to install (from `mcp list`)."),
    client_name: str = typer.Option(..., "--client", "-c", help="The name of the MCP client to configure (e.g., cursor, vscode)."),
    workspace_path: Optional[str] = typer.Option(None, "--workspace", "-w", help="Path to the workspace for client-specific configuration.")
    # Removed python_version option as it wasn't in the rewritten service
) -> None:
    """Installs an MCP server, creates its environment, and updates client configuration."""
    service = get_mcp_service()
    console.print(f"Attempting to install server [cyan]{server_name}[/cyan] for client [green]{client_name}[/green]...")

    # Resolve workspace path if provided
    resolved_workspace_path = os.path.abspath(workspace_path) if workspace_path else None

    try:
        result = service.install_server(
            server_name=server_name,
            client_name=client_name,
            workspace_path=resolved_workspace_path
        )
        console.print(f"[bold green]Success![/bold green] Server [cyan]{result['server_name']}[/cyan] installed successfully.")
        console.print(f"Environment created at: [green]{result['prefix']}[/green]")
        # Add confirmation about config update?

    except ServerAlreadyInstalledError as e:
        console.print(f"[bold yellow]Info:[/bold yellow] {e}")
        raise typer.Exit(code=0) # Exit gracefully
    except (ServerNotFoundError, ClientNotSupportedError, EnvironmentCreationError, PackageInstallationError, ConfigurationError) as e:
        console.print(f"[bold red]Installation Failed:[/bold red] {e}")
        raise typer.Exit(code=1)
    except MCPManagerError as e:
        console.print(f"[bold red]An error occurred during installation:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        import traceback
        traceback.print_exc() # Print full traceback
        raise typer.Exit(code=1)

@server_app.command("update", help="Update an installed server.")
def update_server(
    server_name: str = typer.Argument(..., help="The name of the MCP server to update.")
    # Removed client/workspace options as they weren't used in the rewritten service update
) -> None:
    """Updates the package for an installed MCP server within its environment."""
    service = get_mcp_service()
    console.print(f"Attempting to update server [cyan]{server_name}[/cyan]...")

    try:
        result = service.update_server(server_name=server_name)
        console.print(f"[bold green]Success![/bold green] Server [cyan]{result['server_name']}[/cyan] updated successfully in [green]{result['prefix']}[/green].")

    except ServerNotInstalledError as e:
        console.print(f"[bold red]Update Failed:[/bold red] {e}")
        raise typer.Exit(code=1)
    except ServerNotFoundError as e:
        console.print(f"[bold red]Update Failed:[/bold red] {e} Check if the server is still available in the catalog (`mcp list`).")
        raise typer.Exit(code=1)
    except PackageUpdateError as e:
        console.print(f"[bold red]Update Failed:[/bold red] {e}")
        raise typer.Exit(code=1)
    except MCPManagerError as e:
        console.print(f"[bold red]An error occurred during update:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)

@server_app.command("uninstall", help="Uninstall a server.")
def uninstall_server(
    server_name: str = typer.Argument(..., help="The name of the MCP server to uninstall."),
    client_name: str = typer.Option(..., "--client", "-c", help="The name of the MCP client configuration to update (e.g., cursor, vscode)."),
    workspace_path: Optional[str] = typer.Option(None, "--workspace", "-w", help="Path to the workspace for client-specific configuration.")
) -> None:
    """Uninstalls an MCP server, removing its environment and client configuration."""
    service = get_mcp_service()
    console.print(f"Attempting to uninstall server [cyan]{server_name}[/cyan] for client [green]{client_name}[/green]...")

    # Resolve workspace path if provided
    resolved_workspace_path = os.path.abspath(workspace_path) if workspace_path else None

    # Add confirmation step
    confirm = typer.confirm(f"Are you sure you want to uninstall server '{server_name}'? This will remove its environment and configuration.")
    if not confirm:
        console.print("Uninstallation cancelled.")
        raise typer.Exit()

    try:
        result = service.uninstall_server(
            server_name=server_name,
            client_name=client_name,
            workspace_path=resolved_workspace_path
        )
        console.print(f"[bold green]Success![/bold green] Server [cyan]{result['server_name']}[/cyan] uninstalled successfully.")

    except ServerNotInstalledError as e:
        console.print(f"[bold yellow]Info:[/bold yellow] {e}")
        raise typer.Exit(code=0) # Exit gracefully
    except (EnvironmentRemovalError, ConfigurationError, ClientNotSupportedError) as e:
        console.print(f"[bold red]Uninstallation Failed:[/bold red] {e}")
        raise typer.Exit(code=1)
    except MCPManagerError as e:
        console.print(f"[bold red]An error occurred during uninstallation:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)

@server_app.command("status", help="List installed servers and their status.")
def list_installed(
    client_name: Optional[str] = typer.Option(None, "--client", "-c", help="Filter status based on configuration for a specific client."),
    workspace_path: Optional[str] = typer.Option(None, "--workspace", "-w", help="Path to the workspace for client-specific configuration (requires --client).")
) -> None:
    """Lists installed MCP servers, their environment paths, and configuration status."""
    service = get_mcp_service()

    if workspace_path and not client_name:
        console.print("[bold red]Error:[/bold red] --workspace option requires --client option to be specified.")
        raise typer.Exit(code=1)

    # Resolve workspace path if provided
    resolved_workspace_path = os.path.abspath(workspace_path) if workspace_path else None

    try:
        servers = service.list_installed_servers(client_name=client_name, workspace_path=resolved_workspace_path)

        if not servers:
            console.print("[yellow]No installed MCP servers found.[/yellow]")
            if client_name:
                console.print(f"(Searched within context of client: [green]{client_name}[/green] ",
                              f"and workspace: [yellow]{resolved_workspace_path or 'Global'}[/yellow])")
            return

        table = Table(title="Installed MCP Servers Status")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="yellow")
        table.add_column("Version", style="magenta")
        table.add_column("Environment Path", style="green")
        if client_name:
            table.add_column(f"Configured ({client_name})", style="blue")

        for server in servers:
            row = [
                server["name"],
                server.get("status", "Unknown"),
                server.get("version", "N/A"),
                server.get("prefix", "N/A"),
            ]
            if client_name:
                configured = server.get("configured_for_client", "N/A")
                if isinstance(configured, bool):
                    row.append("[green]Yes[/green]" if configured else "[red]No[/red]")
                else:
                    row.append(f"[yellow]{configured}[/yellow]") # For mismatch messages

            table.add_row(*row)

        console.print(table)

    except (ClientNotSupportedError, ConfigurationError) as e:
        console.print(f"[bold red]Error checking status:[/bold red] {e}")
        raise typer.Exit(code=1)
    except MCPManagerError as e:
        console.print(f"[bold red]Error retrieving status:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)

@server_app.command("start", help="Start an installed MCP server.")
def start_server(
    server_name: str = typer.Argument(..., help="The name of the installed MCP server to start."),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port number for the server to listen on."),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host address for the server to bind to."),
    background: bool = typer.Option(False, "--background", "-b", help="Run the server process in the background.")
) -> None:
    """Starts the specified MCP server process in its conda environment."""
    service = get_mcp_service()
    console.print(f"Attempting to start server [cyan]{server_name}[/cyan]...")

    conda_executable = shutil.which("conda")
    if not conda_executable:
        console.print("[bold red]Error:[/bold red] Could not find conda executable in PATH.")
        raise typer.Exit(code=1)

    try:
        # 1. Find server environment prefix
        prefix = service.env_manager.get_environment_prefix(server_name)
        if not service.env_manager.environment_exists(server_name):
            raise ServerNotInstalledError(f"Server '{server_name}' environment not found at {prefix}. Please install it first.")

        # 2. Determine server entry point (package name)
        # Assumption: Entry point is 'python -m <package_name>'
        # This might need adjustment based on actual server package structure
        try:
            package_name = service.catalog.get_server_package_name(server_name)
        except ServerNotFoundError:
            # If not in catalog, maybe we can infer from environment? Risky.
            # For now, rely on catalog info.
            console.print(f"[bold red]Error:[/bold red] Cannot determine package name for server '{server_name}' from catalog.")
            raise typer.Exit(code=1)

        # 3. Construct the command
        command = [
            conda_executable,
            "run",
            "--prefix",
            prefix,
            "python",
            "-m",
            package_name,
        ]
        # Add host/port if provided (assuming server accepts them)
        command.extend(["--host", host])
        if port is not None:
            command.extend(["--port", str(port)])

        console.print(f"Running command: {' '.join(command)}")

        # 4. Execute the process
        if background:
            console.print(f"Starting server [cyan]{server_name}[/cyan] in the background...")
            # Use start_new_session=True for detaching
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            console.print(f"[green]Server process started in background (PID: {process.pid}).[/green]")
            # Note: We don't wait or capture output for background processes here.
            # Proper background process management (monitoring, stopping) is complex and out of scope for this basic start command.
        else:
            console.print(f"Starting server [cyan]{server_name}[/cyan] in the foreground (Press Ctrl+C to stop)...")
            # Run and stream output
            process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)
            try:
                process.wait() # Wait for the process to finish or be interrupted
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping server...[/yellow]")
                process.terminate() # Send SIGTERM
                try:
                    process.wait(timeout=5) # Wait a bit for graceful shutdown
                except subprocess.TimeoutExpired:
                    process.kill() # Force kill if needed
                console.print("[green]Server stopped.[/green]")
            finally:
                if process.returncode is not None and process.returncode != 0:
                    console.print(f"[yellow]Server exited with code {process.returncode}.[/yellow]")

    except (ServerNotInstalledError, ServerNotFoundError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except MCPManagerError as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)

# --- Entry Points --- #

def conda_plugin(args: List[str]) -> int:
    """
    Entry point for MCP commands when called via conda plugin mechanism.
    """
    # Remove the first argument if it's 'mcp' (when called as 'conda mcp ...')
    # Note: Conda plugin handling might vary; adjust as needed.
    processed_args = args[1:] if args and args[0] == 'mcp' else args
    try:
        app(processed_args)
        return 0
    except typer.Exit as e:
        return e.exit_code
    except Exception:
        # Catch unexpected errors during app execution
        console.print_exception(show_locals=False) # Print traceback
        return 1

def main() -> int:
    """Direct entry point for MCP commands (e.g., when called via script)."""
    import sys
    try:
        app(sys.argv[1:])
        return 0
    except typer.Exit as e:
        return e.exit_code
    except Exception:
        console.print_exception(show_locals=False)
        return 1

if __name__ == "__main__":
    sys.exit(main())


