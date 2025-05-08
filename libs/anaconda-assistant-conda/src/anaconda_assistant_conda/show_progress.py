import time
from rich.progress import Progress
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel

console = Console()


def show_progress():
    # outer status bar and progress bar
    status = console.status("Not started")
    progress = Progress(transient=True)

    with Live(
        Group(status, progress), console=console
    ):  # Optionally: you can remove the `Panel(...)` so just `Live(Group(...))`
        for status_name in ("status1", "status2", "status3"):
            status.update(f"[bold green]Status = {status_name}")
            task_id = progress.add_task(f"Working on task for {status_name}")

            for i in progress.track(range(25), task_id=task_id):
                time.sleep(0.1)
            progress.remove_task(task_id)

        status.update("[bold green]Status = Done")
