from __future__ import annotations

from datetime import date, datetime
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from .models import Task

DEFAULT_DB_PATH = Path("tasks.json")


def load_tasks(db_path: Path = DEFAULT_DB_PATH) -> list[Task]:
    if not db_path.exists():
        return []

    try:
        with db_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Warning: tasks.json is corrupted. Starting fresh.")
        return []

    # Defensive: if file is not a list, treat as corrupted
    if not isinstance(data, list):
        print("Warning: tasks.json has invalid format. Starting fresh.")
        return []

    tasks: list[Task] = []
    for item in data:
        if isinstance(item, dict):
            try:
                due_s = item.get("due")
                if due_s:
                    item["due"] = date.fromisoformat(due_s)
            except ValueError:
                item["due"] = None

            created_at_s = item.get("created_at")
            if not created_at_s:
                continue
            item["created_at"] = datetime.fromisoformat(created_at_s)

            try:
                completed_at_s = item.get("completed_at")
                if completed_at_s:
                    item["completed_at"] = datetime.fromisoformat(completed_at_s)
            except ValueError:
                item["completed_at"] = None

            try:

                tasks.append(Task(**item))
            except TypeError:
                # Skip bad entries instead of crashing
                continue
    return tasks

def task_to_json_dict(tasks:Task)->dict[str,Any]:
    data = []
    for t in tasks:
        d = asdict(t)

        if d["due"] is not None:
            # due is a datetime.date; store as ISO string
            d["due"] = d["due"].isoformat()

        if d.get("created_at") is not None:        
            d["created_at"] = d["created_at"].isoformat()
        else:
            d["created_at"] = None

        if d.get("completed_at"):
            d["completed_at"] = d["completed_at"].isoformat()

        data.append(d)
    return d

def save_tasks(tasks: list[Task], db_path: Path = DEFAULT_DB_PATH) -> None:

    data=task_to_json_dict(tasks=tasks)
    with db_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
