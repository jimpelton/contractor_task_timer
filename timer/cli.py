"""Command-line interface for timer app using Click."""

import click

from timer import __version__
from timer.config import get_config, set_data_path, get_data_path
from timer.core.timer import start_timer
from timer.storage.json_store import (
    get_active_timer,
    save_active_timer,
    clear_active_timer,
    get_entries,
    save_entry,
    delete_entry,
)
from timer.reports.export import (
    filter_entries,
    export_to_csv,
    export_to_json,
    generate_summary,
)


@click.group()
@click.version_option(version=__version__)
def cli():
    """Timer CLI - Track time for subtasks."""
    pass


@cli.command()
@click.argument("name")
@click.option("-d", "--description", default="", help="Task description")
@click.option(
    "-t", "--tag", multiple=True, help="Add tags (can be used multiple times)"
)
def start(name: str, description: str, tag: tuple):
    """Start timing a new task."""
    # Check if there's already an active timer
    active = get_active_timer()
    if active:
        click.echo(f"❌ Timer already running for '{active.task_name}'")
        click.echo(f"   Elapsed: {active.elapsed_formatted}")
        click.echo("   Use 'timer stop' first or 'timer status' to check.")
        return

    # Start new timer
    timer = start_timer(name, description=description, tags=list(tag))
    save_active_timer(timer)

    click.echo(f"⏱️  Started timer for '{name}'")
    if description:
        click.echo(f"   Description: {description}")
    if tag:
        click.echo(f"   Tags: {', '.join(tag)}")


@cli.command()
def stop():
    """Stop the active timer and save the entry."""
    active = get_active_timer()
    if not active:
        click.echo("❌ No active timer running.")
        click.echo("   Use 'timer start <name>' to start one.")
        return

    # Stop and save
    task = active.stop()
    save_entry(task)
    clear_active_timer()

    click.echo(f"✅ Stopped timer for '{task.task_name}'")
    click.echo(f"   Duration: {task.duration_formatted}")
    click.echo(f"   Entry ID: {task.id[:8]}...")


@cli.command()
def pause():
    """Pause the active timer."""
    active = get_active_timer()
    if not active:
        click.echo("❌ No active timer running.")
        return

    if active.paused:
        click.echo(f"⏸️  Timer for '{active.task_name}' is already paused.")
        click.echo(f"   Elapsed before pause: {active.elapsed_formatted}")
        click.echo("   Use 'timer resume' to continue.")
        return

    active.pause()
    save_active_timer(active)

    click.echo(f"⏸️  Paused timer for '{active.task_name}'")
    click.echo(f"   Elapsed: {active.elapsed_formatted}")


@cli.command()
def resume():
    """Resume a paused timer."""
    active = get_active_timer()
    if not active:
        click.echo("❌ No active timer running.")
        return

    if not active.paused:
        click.echo(f"▶️  Timer for '{active.task_name}' is already running.")
        click.echo(f"   Elapsed: {active.elapsed_formatted}")
        return

    active.resume()
    save_active_timer(active)

    click.echo(f"▶️  Resumed timer for '{active.task_name}'")
    click.echo(f"   Elapsed: {active.elapsed_formatted}")


@cli.command()
def status():
    """Show current timer status."""
    active = get_active_timer()
    if not active:
        click.echo("No active timer.")

        # Show recent entries
        entries = get_entries()
        if entries:
            click.echo(
                f"\nLast entry: '{entries[-1].task_name}' ({entries[-1].duration_formatted})"
            )
        return

    status_icon = "⏸️ " if active.paused else "⏱️ "
    status_text = "PAUSED" if active.paused else "RUNNING"

    click.echo(f"{status_icon} {active.task_name} [{status_text}]")
    click.echo(f"   Started: {active.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"   Elapsed: {active.elapsed_formatted}")

    if active.description:
        click.echo(f"   Description: {active.description}")
    if active.tags:
        click.echo(f"   Tags: {', '.join(active.tags)}")


@cli.command("list")
@click.option("--today", is_flag=True, help="Show only today's entries")
@click.option("--week", is_flag=True, help="Show only this week's entries")
@click.option("-n", "--limit", default=10, help="Number of entries to show")
def list_entries(today: bool, week: bool, limit: int):
    """List recorded time entries."""
    entries = get_entries()
    entries = filter_entries(entries, today=today, week=week)

    if not entries:
        click.echo("No entries found.")
        return

    # Sort by start time, most recent first
    entries = sorted(entries, key=lambda e: e.start_time, reverse=True)[:limit]

    click.echo(f"{'ID':<10} {'Task':<20} {'Duration':<12} {'Date':<12}")
    click.echo("-" * 56)

    for entry in entries:
        click.echo(
            f"{entry.id[:8]:<10} "
            f"{entry.task_name[:20]:<20} "
            f"{entry.duration_formatted:<12} "
            f"{entry.start_time.strftime('%Y-%m-%d'):<12}"
        )

    # Show summary
    summary = generate_summary(entries)
    click.echo("-" * 56)
    click.echo(
        f"Total: {summary['total_formatted']} across {summary['total_entries']} entries"
    )


@cli.command()
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["csv", "json"]),
    default="csv",
    help="Export format",
)
@click.option("--today", is_flag=True, help="Export only today's entries")
@click.option("--week", is_flag=True, help="Export only this week's entries")
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file (prints to stdout if not specified)",
)
def report(fmt: str, today: bool, week: bool, output: str):
    """Export time entries as CSV or JSON."""
    entries = get_entries()
    entries = filter_entries(entries, today=today, week=week)

    if not entries:
        click.echo("No entries found.")
        return

    if fmt == "csv":
        content = export_to_csv(entries)
    else:
        content = export_to_json(entries)

    if output:
        with open(output, "w") as f:
            f.write(content)
        click.echo(f"Exported {len(entries)} entries to {output}")
    else:
        click.echo(content)


@cli.command()
@click.argument("entry_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete(entry_id: str, yes: bool):
    """Delete a time entry by ID."""
    # Find entries that match (partial ID)
    entries = get_entries()
    matches = [e for e in entries if e.id.startswith(entry_id)]

    if not matches:
        click.echo(f"❌ No entry found matching '{entry_id}'")
        return

    if len(matches) > 1:
        click.echo(f"❌ Multiple entries match '{entry_id}':")
        for e in matches:
            click.echo(f"   {e.id[:8]} - {e.task_name}")
        click.echo("Use a more specific ID.")
        return

    entry = matches[0]

    if not yes:
        click.confirm(
            f"Delete entry '{entry.task_name}' ({entry.duration_formatted})?",
            abort=True,
        )

    delete_entry(entry.id)
    click.echo(f"🗑️  Deleted entry '{entry.task_name}'")


@cli.command()
@click.option("--data-path", type=click.Path(), help="Set custom data path")
def config(data_path: str):
    """View or set configuration."""
    if data_path:
        new_path = set_data_path(data_path)
        click.echo(f"✅ Data path set to: {new_path}")
    else:
        cfg = get_config()
        click.echo("Current configuration:")
        click.echo(f"  Data path: {cfg['data_path']}")
        click.echo(f"  (Resolved: {get_data_path()})")


if __name__ == "__main__":
    cli()
