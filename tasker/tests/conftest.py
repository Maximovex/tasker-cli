import pytest
from tasker.storage import save_tasks
from tasker.models import Task
from datetime import date,datetime, timedelta, timezone


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "tasks.json"

@pytest.fixture
def db_sqlite(tmp_path):
    return tmp_path/"tasks.db"


@pytest.fixture
def two_tasks(db_path):
    today = date.today()
    tasks = [
        Task(
            id=1,
            title="A",
            due=today - timedelta(days=1),
            created_at=datetime(2026, 1, 29, tzinfo=timezone.utc),
        ),
        Task(
            id=2,
            title="B",
            due=today + timedelta(days=1),
            created_at=datetime(2026, 1, 29, tzinfo=timezone.utc),
        ),
    ]
    save_tasks(tasks=tasks, db_path=db_path)
    return tasks
