from __future__ import annotations
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path

from .models import Task
from .storage import save_tasks


def next_id(tasks: list[Task]) -> int:
    return 1 if not tasks else max(t.id for t in tasks) + 1


def add_task(
    tasks: list[Task],
    title: str,
    *,
    db_path: Path,
    due: str | None = None,
) -> str:
    title = title.strip()
    if not title:
        return "Title cannot be empty."
    try:
        due_date = date.fromisoformat(due) if due else None
    except ValueError:
        return "Invalid due date. Use YYYY-MM-DD."
    tid = next_id(tasks)
    tasks.append(
        Task(
            id=tid,
            title=title,
            created_at=datetime.now(timezone.utc),
            due=due_date,
            done=False,
        )
    )
    save_tasks(tasks, db_path=db_path)
    return f"Added #{tid}: {title}"


def mark_done(tasks: list[Task], tid: int, *, db_path: Path) -> str:
    for t in tasks:
        if t.id == tid:
            if t.done:
                return f"Task #{tid} is already done."
            t.done = True
            t.completed_at = datetime.now(timezone.utc)
            save_tasks(tasks, db_path=db_path)
            return f"Marked #{tid} as done."
    return f"No task with id {tid}"


def delete_task(tasks: list[Task], tid: int, *, db_path: Path) -> str:
    for i, t in enumerate(tasks):
        if t.id == tid:
            removed = tasks.pop(i)
            save_tasks(tasks, db_path=db_path)
            return f"Deleted #{tid}: {removed.title}"
    return f"No task with id {tid}"


def edit_task(tasks: list[Task], tid: int, new_title: str, *, db_path: Path) -> str:
    new_title = new_title.strip()
    if not new_title:
        return "Title cannot be empty."

    for t in tasks:
        if t.id == tid:
            old = t.title
            t.title = new_title
            save_tasks(tasks, db_path=db_path)
            return f"Edited #{tid}: {old} -> {new_title}"
    return f"No task with id {tid}"


def list_tasks(
    tasks: list[Task],
    *,
    show: str = "all",  # "all" | "done" | "open"
    search: str | None = None,  # substring match on title
) -> list[str]:
    filtered = tasks

    if show == "done":
        filtered = [t for t in filtered if t.done]
    elif show == "open":
        filtered = [t for t in filtered if not t.done]

    if search:
        q = search.lower()
        filtered = [t for t in filtered if q in t.title.lower()]

    if not filtered:
        return ["No tasks match."]

    lines: list[str] = []
    for t in filtered:
        box = "x" if t.done else " "
        lines.append(f"{t.id:>3}. [{box}] {t.title}")
    return lines
