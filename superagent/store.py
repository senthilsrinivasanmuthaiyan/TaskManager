import json
import os
import sqlite3
from datetime import datetime, timezone
from .config import get_settings


def _connect():
    path = get_settings().database_path
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("""CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        project_key TEXT,
        run_type TEXT NOT NULL,
        status TEXT NOT NULL,
        request TEXT NOT NULL,
        result TEXT
    )""")
    return db


def save_run(project_key: str | None, run_type: str, status: str, request: str, result: dict) -> int:
    with _connect() as db:
        cur = db.execute(
            "INSERT INTO runs(created_at, project_key, run_type, status, request, result) VALUES(?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), project_key, run_type, status, request, json.dumps(result)),
        )
        return int(cur.lastrowid)


def recent_runs(limit: int = 30) -> list[dict]:
    with _connect() as db:
        rows = db.execute(
            "SELECT id,created_at,project_key,run_type,status,request,result FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [{"id": r[0], "created_at": r[1], "project_key": r[2], "run_type": r[3],
             "status": r[4], "request": r[5], "result": json.loads(r[6]) if r[6] else None} for r in rows]
