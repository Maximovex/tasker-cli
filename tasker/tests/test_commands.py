from datetime import date
from tasker.commands import add_task,mark_done,delete_task,edit_task
from tasker.storage import load_tasks,save_tasks
from tasker.models import Task


def test_add(db_path):
    tasks=[]
    msg=add_task(tasks=tasks,title= "Read book",db_path=db_path)
    loaded=load_tasks(db_path=db_path)
    assert len(loaded) ==1
    assert "Added #1" in msg
    assert loaded[0].title=="Read book"

def test_add_increment(two_tasks,db_path):
    msg =add_task(tasks=two_tasks,title="C",db_path=db_path)
    tasks=load_tasks(db_path=db_path)
    assert [t.id for t in tasks]==[1,2,3]
    assert "Added #3" in msg

def test_mark_done(db_path):
    tasks=[Task(id=1,title="Read book",done=False,created_at=date.today())]
    save_tasks(tasks,db_path=db_path)
    msg=mark_done(tasks=tasks,tid=1,db_path=db_path)
    loaded=load_tasks(db_path=db_path)
    assert loaded[0].done is True
    assert "Marked #1" in msg

def test_delete_task(two_tasks,db_path):
    msg=delete_task(tasks=two_tasks,tid=1,db_path=db_path)
    loaded=load_tasks(db_path=db_path)
    assert "Deleted #1" in msg
    assert [t.id for t in loaded]==[2]

def test_edit(two_tasks,db_path):
    msg=edit_task(two_tasks,tid=1,new_title="",db_path=db_path)
    tasks=load_tasks(db_path=db_path)
    assert "Title cannot be empty" in msg
    assert tasks[0].title=="A"
    assert [(t.id,t.title)for t in tasks]==[(1,"A"),(2,"B")]

    