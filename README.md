# Tasker

A fast, lightweight, feature-rich command-line task management tool written in Python. `tasker` helps you track tasks, set due dates, filter and sort lists, and export data in multiple formats with support for both JSON and SQLite storage backends.

---

## Features

- **Flexible Storage Backends**: Automatically switches between **JSON** (`.json`) and **SQLite** (`.db`, `.sqlite`, `.sqlite3`) storage based on the file extension.
- **Task Management**: Create, edit, list, mark done/undone, delete, and batch-clear completed tasks.
- **Due Dates & Tracking**: Attach due dates to tasks and track creation and completion timestamps.
- **Advanced Filtering**: Filter tasks by status (`--done`, `--open`), time window (`--today`, `--overdue`), or keyword search (`--search`).
- **Sorting Options**: Sort tasks by `id`, `title`, `due` date, status (`done`), `created` date, or `completed` date, with optional `--reverse` sorting.
- **Output Formats**: View task lists in formatted tables or raw JSON export (`--format json`).
- **CLI Shell Auto-completion**: Integrated `argcomplete` support for tab completion in bash/zsh.

---

## Installation

### Requirements

- Python **>= 3.14** (or Python 3.10+ compatible environment)

### Install Locally

Clone the repository and install in editable mode or build using `pip` or `uv`:

```bash
git clone https://github.com/Maximovex/tasker-cli.git
cd tasker
pip install -e .
```

Or using `uv`:

```bash
uv pip install -e .
```

---

## Quick Start & Usage

`tasker` can be invoked either directly via the installed binary `tasker` or using Python module execution `python -m tasker`.

### Global Arguments

- `--db PATH`: Specify database file path (default: `tasks.json`). File extensions ending in `.db`, `.sqlite`, or `.sqlite3` will automatically activate the SQLite engine.
- `--format {table,json}`: Choose output format for task lists (default: `table`).

---

### Commands

#### 1. Add a Task
Add a new task with an optional due date (`YYYY-MM-DD`).

```bash
# Basic task
tasker add Buy groceries

# Task with due date
tasker add Complete report --due 2026-08-15
```

#### 2. List Tasks
View tasks with filtering, sorting, or JSON formatting.

```bash
# List all tasks
tasker list

# Show only open tasks
tasker list --open

# Show completed tasks
tasker list --done

# Filter by due status
tasker list --today
tasker list --overdue

# Search by keyword
tasker list --search "groceries"

# Sort tasks by due date in reverse order
tasker list --sort due --reverse

# Output as JSON
tasker list --format json
```

#### 3. Mark Done / Undone
Toggle completion state of a task by ID.

```bash
# Mark task #1 as completed
tasker done 1

# Re-open completed task #1
tasker undone 1
```

#### 4. Edit a Task
Update the title of an existing task.

```bash
tasker edit 1 Buy groceries and fruits
```

#### 5. Delete Tasks
Delete a task by ID or clear all completed tasks.

```bash
# Delete specific task
tasker delete 1

# Clear all completed tasks
tasker clear --done
```

---

## Dual Storage Backends

`tasker` seamlessly handles JSON and SQLite storage depending on the `--db` option provided:

- **JSON Backend (default)**: Used when database path is `tasks.json` or ends with `.json`. Stores tasks in a human-readable JSON array.
- **SQLite Backend**: Used when database file extension is `.db`, `.sqlite`, or `.sqlite3`. Stores tasks in an indexed SQLite table.

```bash
# Use SQLite database
tasker --db my_tasks.sqlite add "SQLite Task"
tasker --db my_tasks.sqlite list
```

---

## Shell Auto-Completion

`tasker` uses [`argcomplete`](https://github.com/kislyuk/argcomplete) for command line tab completion.

To enable completion in your current bash session:

```bash
eval "$(register-python-argcomplete tasker)"
```

---

## Running Tests

Run the test suite using `pytest`:

```bash
pytest
```
