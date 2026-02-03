from datetime import date, datetime, timezone
import sqlite3
from pathlib import Path

from tasker.models import Task


class TaskRepository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(
            str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                due TEXT,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """
        )
        self.conn.commit()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        created_at = datetime.fromisoformat(row["created_at"])
        completed_at = (
            datetime.fromisoformat(row["completed_at"])
            if row["completed_at"] is not None
            else None
        )
        due = date.fromisoformat(row["due"]) if row["due"] is not None else None
        return Task(
            id=row["id"],
            title=row["title"],
            done=bool(row["done"]),
            completed_at=completed_at,
            created_at=created_at,
            due=due,
        )

    def all(self) -> list[Task]:
        cur = self.conn.execute("SELECT * FROM tasks ORDER BY id")
        return [self._row_to_task(r) for r in cur.fetchall()]

    def close(self) -> None:
        self.conn.close()

    def add_task(
        self, title: str, *, due: date | None = None, created_at: datetime | None = None
    ) -> Task:

        created_at = created_at or datetime.now(timezone.utc)
        created_s = created_at.isoformat()

        due_s = due.isoformat() if due else None
        cur = self.conn.execute(
            "INSERT INTO tasks (title,due,created_at) VALUES (?,?,?)",
            (
                title,
                due_s,
                created_s,
            ),
        )
        self.conn.commit()
        return Task(
            id=cur.lastrowid,
            title=title,
            due=due,
            created_at=created_at,
            done=False,
            completed_at=None,
        )

    def update_task(self, t: Task) -> bool:

        due = t.due.isoformat() if t.due else None
        created_s = t.created_at.isoformat()
        completed_s = datetime.now(timezone.utc).isoformat() if t.done is True else None

        cur = self.conn.execute(
            "UPDATE tasks SET title=?,due=?,done=?,completed_at=?,created_at=? WHERE id=?",
            (t.title, due, t.done, completed_s, created_s, t.id),
        )
        self.conn.commit()

        return bool(cur.rowcount)

    def delete(self, tid: int) -> bool:
        cur = self.conn.execute("DELETE FROM tasks WHERE id=?", (tid,))
        self.conn.commit()

        return bool(cur.rowcount)

    def mark_done(self, tid: int) -> str:
        completed_s = datetime.now(timezone.utc).isoformat()

        cur = self.conn.execute(
            "UPDATE tasks SET done=1, completed_at=? WHERE id=? AND done=0",
            (
                completed_s,
                tid,
            ),
        )
        self.conn.commit()

        if cur.rowcount == 1:
            return "updated"

        row = self.conn.execute("SELECT done FROM tasks WHERE id=?", (tid,)).fetchone()
        if row is None:
            return "missing"
        elif row["done"] == 1:
            return "already"
        else:
            return "missing"

    def mark_undone(self, tid: int) -> str:

        cur = self.conn.execute(
            "UPDATE tasks SET done=0, completed_at=NULL WHERE id=? AND done=1",
            (tid,),
        )
        self.conn.commit()

        if cur.rowcount == 1:
            return "updated"
        row = self.conn.execute("SELECT done FROM tasks WHERE id=?", (tid,)).fetchone()
        if row is None:
            return "missing"
        elif row["done"] == 0:
            return "already"
        else:
            return "missing"

    def clear_done(self) -> int:
        cur = self.conn.execute("DELETE FROM tasks WHERE done=1")
        self.conn.commit()
        return cur.rowcount

    def list_filtered(
        self,
        *,
        show: str = "all",  # all|done|open
        search: str | None = None,
        sort: str | None = None,  # id|title|due|done|created|completed
        reverse: bool = False,
        overdue: bool = False,
        today: bool = False,
    ) -> list[Task]:

        where = []
        params = []
        rev = "" if reverse is False else " DESC"
        sort_map = {
            "id": f"id{rev}",
            "title": f"LOWER(title){rev}",
            "done": f"done{rev}",
            "created": f"created_at{rev}",
            "completed": f"(completed_at IS NULL){rev}, completed_at{rev}",
            "due": f"(due IS NULL){rev}, due{rev}",
        }
        today_s = date.today().isoformat()
        if show == "done":
            where.append("done = 1")
        elif show == "open":
            where.append("done = 0")

        if overdue:
            where.append("done = 0")
            where.append("due IS NOT NULL")
            where.append("due < ?")
            params.append(today_s)
        elif today:
            where.append("due = ?")
            params.append(today_s)

        if search:
            where.append("LOWER(title) LIKE ?")
            params.append(f"%{search.lower()}%")

        sql = "SELECT * FROM tasks"
        if where:
            sql += " WHERE " + " AND ".join(where)

        if sort and sort in sort_map:
            order = f"ORDER BY {sort_map.get(sort)}"
        else:
            order = "ORDER BY id"

        sql += " " + order

        cur = self.conn.execute(sql, params)
        return [self._row_to_task(r) for r in cur.fetchall()]


if __name__ == "__main__":
    repo = TaskRepository(Path("tmp_tasks.db"))
    repo.add_task("papa")
    print(repo.list_filtered(search="papa"))
    repo.close()
