from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime

@dataclass
class Task:
    id: int
    title: str
    created_at: datetime
    due: date | None = None
    done: bool = False    
    completed_at: datetime|None=None