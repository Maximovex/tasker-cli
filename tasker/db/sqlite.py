from datetime import date, datetime
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

    def add_task(self, title: str, *, due: date | None = None, created_at: datetime | None = None) -> Task:
        pass

    def update_task(self, t: Task) -> bool:
        pass
    
    def delete(self, tid: int) -> bool:
        pass
    
if __name__ == "__main__":
    repo = TaskRepository(Path("tmp_tasks.db"))
    print(repo.all())
    repo.close()
