"""Utilities for managing server processes."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import typer


class ServerManager:
    """Manages the lifecycle of a background server process."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.pid_file = Path.home() / ".cache" / "mcp" / f"{project_name}.pid"
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)

    def get_pid(self) -> int | None:
        """
        Reads and returns the PID from the PID file.
        Returns None if the file doesn't exist or is empty.
        """
        if not self.pid_file.exists():
            return None
        try:
            pid = int(self.pid_file.read_text().strip())
            return pid
        except (OSError, ValueError):
            return None

    def is_running(self) -> bool:
        """Checks if the process with the stored PID is currently running."""
        pid = self.get_pid()
        if not pid:
            return False
        try:
            # Sending signal 0 to a process checks if it exists without killing it.
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def start_server(self, host: str, port: int, debug: bool, reload: bool) -> None:
        """Starts the server as a background process and saves its PID."""
        if self.is_running():
            typer.echo(f"Server '{self.project_name}' is already running.")
            raise typer.Exit()

        # Set environment variables for the subprocess
        env = os.environ.copy()
        env["MCP_SERVER_HOST"] = host
        env["MCP_SERVER_PORT"] = str(port)
        env["MCP_DEBUG"] = str(debug).lower()
        env["MCP_RELOAD"] = str(reload).lower()

        # Command to run the server function directly
        command = [
            sys.executable,
            "-c",
            "from unifi_mcp.server import run_server; run_server()",
        ]

        # Start the process in the background
        process = subprocess.Popen(command, env=env, close_fds=True)

        # Write the new PID to the file
        try:
            self.pid_file.write_text(str(process.pid))
            typer.echo(
                f"Started UniFi MCP server on {host}:{port} (PID: {process.pid})"
            )
        except OSError as e:
            typer.echo(f"Error writing PID file: {e}", err=True)
            process.kill()
            raise typer.Exit(1)

    def stop_server(self) -> None:
        """Stops the running server process using the stored PID."""
        pid = self.get_pid()
        if not pid or not self.is_running():
            typer.echo(f"Server '{self.project_name}' is not running.")
            return

        typer.echo(f"Stopping server '{self.project_name}' (PID: {pid})...")
        try:
            os.kill(pid, signal.SIGTERM)
            # Wait a moment for the process to terminate
            time.sleep(1)
        except OSError:
            # Process might have already died
            pass
        finally:
            if self.pid_file.exists():
                self.pid_file.unlink()
        typer.echo("Server stopped.")

    def get_status(self) -> None:
        """Prints the current status of the server."""
        pid = self.get_pid()
        if self.is_running():
            typer.echo(f"UniFi MCP server is RUNNING (PID: {pid})")
        else:
            typer.echo("UniFi MCP server is STOPPED.")
