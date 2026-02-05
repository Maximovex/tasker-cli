from datetime import date,datetime
from tasker.db import TaskRepository

def test_sort(db_sqlite):
    db=db_sqlite
    repo=TaskRepository(db)
    repo.add_task("a",due=date.today())
    repo.add_task("b",due=date.today())
    repo.add_task("c",due=date.today())
    assert [t.title for t in repo.list_filtered(sort="title")]==["a","b","c"]
    assert [t.title for t in repo.list_filtered(sort="title",reverse=True)]==["c","b","a"]
    repo.close()

def test_list(db_sqlite):
    pass

def test_add(db_sqlite):
    repo=TaskRepository(db_sqlite)
    t=repo.add_task("milk")
    