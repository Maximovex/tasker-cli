# PYTHON_ARGCOMPLETE_OK

from __future__ import annotations
import argparse
from dataclasses import asdict
from datetime import date, datetime, timezone
import json
from tasker.commands import (
    add_task,
    clear_done,
    delete_task,
    edit_task,
    mark_done,
    mark_undone,
)
from tasker.storage import load_tasks, task_to_json_dict
from pathlib import Path

USAGE = """\
Usage:
  python -m tasker add "title"
  python -m tasker list [--done|--open] [--search "text"]
  python -m tasker done <id>
  python -m tasker delete <id>
  python -m tasker edit <id> "new title"
"""


def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="tasks.json", help="Path to JSON database")
    p.add_argument(
        "--format",
        default="table",
        choices=["table", "json"],
        help="Format for list representation, table or json",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("title", nargs="+")
    p_add.add_argument("--due", metavar="YYYY-MM-DD", default=None, help="Due date")

    p_list = sub.add_parser("list")
    group = p_list.add_mutually_exclusive_group()
    group.add_argument("--done", action="store_true")
    p_list.add_argument("--search", metavar="TEXT")
    p_list.add_argument(
        "--sort",
        choices=["id", "title", "due", "done", "created", "completed"],
        default=None,
        help="Sort list output by id, title, done,completed, created or due date",
    )
    group.add_argument("--open", action="store_true")

    group2 = p_list.add_mutually_exclusive_group()
    group2.add_argument("--overdue", action="store_true")
    group2.add_argument("--today", action="store_true")

    p_list.add_argument("--reverse", action="store_true", help="Reverse sorting")

    p_edit = sub.add_parser("edit")
    p_edit.add_argument("id", type=int)
    p_edit.add_argument("title", nargs="+")

    p_done = sub.add_parser("done")
    p_done.add_argument("id", type=int)

    p_undone = sub.add_parser("undone", help="Mark task as not done")
    p_undone.add_argument("id", type=int, help="Task id")

    p_del = sub.add_parser("delete")
    p_del.add_argument("id", type=int)

    p_clear = sub.add_parser("clear", help="Clear tasks")
    p_clear.add_argument("--done", action="store_true", help="Clear completed")

    return p


import argcomplete


def run(argv: list[str]) -> int:
    parser = build_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv[1:])
    db_path = Path(args.db)
    tasks = load_tasks(db_path=db_path)

    cmd = args.cmd

    if cmd == "add":

        title = " ".join(args.title)
        print(add_task(tasks, title, due=args.due, db_path=db_path))
        return 0

    if cmd == "list":
        filtered = tasks

        if args.done:
            filtered = [t for t in filtered if t.done]
        elif args.open:
            filtered = [t for t in filtered if not t.done]

        if args.search:
            q = args.search.lower()
            filtered = [t for t in filtered if q in t.title.lower()]

        today = date.today()
        if args.overdue:
            filtered = [t for t in filtered if t.due and t.due < today and not t.done]
        elif args.today:
            filtered = [t for t in filtered if t.due == today]

        if args.sort == "id":
            filtered = sorted(filtered, key=lambda task: task.id, reverse=args.reverse)
        elif args.sort == "title":
            filtered = sorted(
                filtered, key=lambda task: task.title.lower(), reverse=args.reverse
            )
        elif args.sort == "done":
            filtered = sorted(
                filtered, key=lambda task: task.done, reverse=args.reverse
            )
        elif args.sort == "due":
            filtered = sorted(
                filtered,
                key=lambda task: (task.due is None, task.due or date.max),
                reverse=args.reverse,
            )
        elif args.sort == "created":
            filtered = sorted(
                filtered,
                key=lambda task: task.created_at,
                reverse=args.reverse,
            )
        elif args.sort == "completed":
            filtered = sorted(
                filtered,
                key=lambda task: (
                    task.completed_at is None,
                    task.completed_at or datetime.max.replace(tzinfo=timezone.utc),
                ),
                reverse=args.reverse,
            )

        if args.format == "table":
            if not filtered:
                print("No tasks match")
                return 0

            for t in filtered:
                box = "x" if t.done else " "
                due = t.due.isoformat() if t.due else "-"
                created_at = t.created_at.date().isoformat()
                completed_at = (
                    t.completed_at.date().isoformat() if t.completed_at else "-"
                )
                print(
                    f"{t.id:>3}. [{box}] {t.title} (due: {due}, created at: {created_at}, completed at: {completed_at})"
                )
        else:
            print(json.dumps([task_to_json_dict(t) for t in filtered], indent=2))

        return 0

    if cmd in {"done", "delete"}:

        tid = args.id
        msg = (
            mark_done(tasks, tid, db_path=db_path)
            if cmd == "done"
            else delete_task(tasks, tid, db_path=db_path)
        )
        print(msg)
        return 0 if not msg.startswith("No task") else 1

    if cmd == "edit":

        tid = args.id
        new_title = " ".join(args.title)
        msg = edit_task(tasks, tid, new_title, db_path=db_path)
        print(msg)
        return 0 if not msg.startswith("No task") else 1
    
    if cmd == "undone":
        msg = mark_undone(tasks, args.id, db_path=db_path)
        print(msg)
        return 0 if not msg.startswith("No task") else 1

    if cmd == "clear":
        if args.done:
            msg = clear_done(tasks=tasks, db_path=db_path)
            print(msg)
            return 0 if not msg.startswith("No completed") else 1
        else:
            print("Use --done to clear completed tasks")
            return 1

    print(f"Unknown command: {cmd}")
    print(USAGE)
    return 1


import sys


def main() -> None:
    raise SystemExit(run(sys.argv))
