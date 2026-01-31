import subprocess, json, sys


def test_cli(db_path):
    r1 = subprocess.run(
        [
            sys.executable,
            "-m",
            "tasker",
            "--db",
            str(db_path),
            "add",
            "milk",
        ],
        capture_output=True,
        text=True,
    )
    r2 = subprocess.run(
        [
            sys.executable,
            "-m",
            "tasker",
            "--db",
            str(db_path),
            "--format",
            "json",
            "list",
        ],
        capture_output=True,
        text=True,
    )

    assert r1.returncode == 0, (r1.stdout, r1.stderr)
    assert r2.returncode == 0, (r2.stdout, r2.stderr)
    data = json.loads(r2.stdout)

    assert any(t["title"] == "milk" for t in data)


def test_overdue(two_tasks, db_path):

    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "tasker",
            "--db",
            str(db_path),
            "--format",
            "json",
            "list",
            "--overdue",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
    data = json.loads(r.stdout)
    assert [t["id"] for t in data]==[1]
