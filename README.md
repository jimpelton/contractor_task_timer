# Timer CLI

A command-line timer app for tracking time spent on subtasks.

## Installation

```bash
uv sync
```

## Usage

```bash
# Start a timer
timer start "task-name" -d "Optional description" -t tag1 -t tag2

# Check status
timer status

# Pause/resume
timer pause
timer resume

# Stop and save entry
timer stop

# List entries
timer list --today
timer list --week
timer list -n 20

# Export
timer report --format csv -o timesheet.csv
timer report --format json

# Configuration
timer config                        # View config
timer config --data-path ~/timers   # Set data location

# Delete entry
timer delete <entry-id>
```

## Configuration

Config is stored in `~/.timer/config.json`. Timer data (entries, active timer) is stored at the configured `data_path` (defaults to `~/.timer/data`).
