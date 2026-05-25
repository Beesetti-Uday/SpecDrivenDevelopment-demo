from __future__ import annotations

import calendar
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

VALID_RECURRENCES = {"daily", "weekly", "monthly"}


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def format_date(value: date) -> str:
    return value.isoformat()


def next_occurrence(current: date, recurrence: str) -> date:
    if recurrence == "daily":
        return current + timedelta(days=1)
    if recurrence == "weekly":
        return current + timedelta(weeks=1)
    if recurrence == "monthly":
        month = current.month + 1
        year = current.year
        if month > 12:
            month = 1
            year += 1
        day = min(current.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
    raise ValueError(f"Unsupported recurrence: {recurrence}")


class Storage:
    def __init__(self, path: Optional[Path | str] = None):
        self.path = Path(path) if path else self.default_path()
        self.data = self._load()

    @staticmethod
    def default_path() -> Path:
        return Path.home() / ".config" / "superpower-terminal-todo" / "data.json"

    def _load(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.path.exists():
            return {"tasks": [], "journals": [], "followups": []}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return {
            "tasks": raw.get("tasks", []),
            "journals": raw.get("journals", []),
            "followups": raw.get("followups", []),
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def _next_id(self, collection: str) -> int:
        values = [item["id"] for item in self.data.get(collection, []) if isinstance(item.get("id"), int)]
        return max(values, default=0) + 1

    def _find(self, collection: str, item_id: int) -> Optional[Dict[str, Any]]:
        return next((item for item in self.data.get(collection, []) if item.get("id") == item_id), None)

    def add_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        recurrence: Optional[str] = None,
    ) -> Dict[str, Any]:
        if recurrence and recurrence not in VALID_RECURRENCES:
            raise ValueError(f"Recurrence must be one of {sorted(VALID_RECURRENCES)}")
        task_id = self._next_id("tasks")
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "status": "pending",
            "due_date": due_date,
            "recurrence": recurrence,
            "journal_ids": [],
            "follow_up_ids": [],
            "last_completed": None,
        }
        self.data["tasks"].append(task)
        self.save()
        return task

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        recurrence: Optional[str] = None,
    ) -> Dict[str, Any]:
        task = self._require_task(task_id)
        if title is not None:
            task["title"] = title
        if description is not None:
            task["description"] = description
        if due_date is not None:
            task["due_date"] = due_date
        if recurrence is not None:
            if recurrence not in VALID_RECURRENCES:
                raise ValueError(f"Recurrence must be one of {sorted(VALID_RECURRENCES)}")
            task["recurrence"] = recurrence
        self.save()
        return task

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        task = self._require_task(task_id)
        if task.get("recurrence"):
            current = parse_date(task.get("due_date", date.today().isoformat()))
            task["last_completed"] = date.today().isoformat()
            task["due_date"] = format_date(next_occurrence(current, task["recurrence"]))
            task["status"] = "pending"
        else:
            task["status"] = "completed"
        self.save()
        return task

    def delete_task(self, task_id: int) -> None:
        task = self._require_task(task_id)
        self.data["tasks"] = [item for item in self.data["tasks"] if item.get("id") != task_id]
        self.save()

    def list_tasks(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        tasks = self.data["tasks"]
        if not include_completed:
            tasks = [task for task in tasks if task.get("status") != "completed" or task.get("recurrence")]
        return sorted(tasks, key=lambda item: (item.get("due_date") or "", item.get("id")))

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        return self._find("tasks", task_id)

    def add_journal(self, title: str, content: str, task_id: Optional[int] = None) -> Dict[str, Any]:
        if task_id is not None:
            self._require_task(task_id)
        journal_id = self._next_id("journals")
        journal = {
            "id": journal_id,
            "title": title,
            "content": content,
            "date": date.today().isoformat(),
            "task_id": task_id,
        }
        self.data["journals"].append(journal)
        if task_id is not None:
            task = self._require_task(task_id)
            task.setdefault("journal_ids", []).append(journal_id)
        self.save()
        return journal

    def list_journals(self) -> List[Dict[str, Any]]:
        return sorted(self.data["journals"], key=lambda item: item.get("date", ""), reverse=True)

    def get_journal(self, journal_id: int) -> Optional[Dict[str, Any]]:
        return self._find("journals", journal_id)

    def add_followup(self, task_id: int, note: str, due_date: Optional[str] = None) -> Dict[str, Any]:
        self._require_task(task_id)
        followup_id = self._next_id("followups")
        followup = {
            "id": followup_id,
            "task_id": task_id,
            "note": note,
            "due_date": due_date,
            "status": "pending",
            "created_at": date.today().isoformat(),
        }
        self.data["followups"].append(followup)
        task = self._require_task(task_id)
        task.setdefault("follow_up_ids", []).append(followup_id)
        self.save()
        return followup

    def list_followups(self, task_id: Optional[int] = None) -> List[Dict[str, Any]]:
        followups = self.data["followups"]
        if task_id is not None:
            followups = [item for item in followups if item.get("task_id") == task_id]
        return sorted(followups, key=lambda item: (item.get("due_date") or "", item.get("id")))

    def recent_journals(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.list_journals()[:limit]

    def pending_followups(self, task_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return [item for item in self.list_followups(task_id=task_id) if item.get("status") != "completed"]

    def recurring_tasks(self) -> List[Dict[str, Any]]:
        return [task for task in self.data["tasks"] if task.get("recurrence")]

    def dashboard_summary(self, upcoming_days: int = 3) -> Dict[str, Any]:
        today = date.today()
        due_soon = []
        for task in self.list_tasks(include_completed=True):
            due_date = task.get("due_date")
            if due_date:
                parsed = parse_date(due_date)
                if parsed <= today + timedelta(days=upcoming_days) and task.get("status") != "completed":
                    due_soon.append(task)
        return {
            "pending_tasks": [task for task in self.list_tasks() if task.get("status") != "completed" or task.get("recurrence")],
            "due_soon": due_soon,
            "recurring_tasks": self.recurring_tasks(),
            "recent_journals": self.recent_journals(),
            "pending_followups": self.pending_followups(),
        }

    def task_context(self, task_id: int) -> Dict[str, Any]:
        task = self._require_task(task_id)
        return {
            "task": task,
            "journals": [journal for journal in self.list_journals() if journal.get("task_id") == task_id],
            "followups": self.pending_followups(task_id=task_id),
        }

    def get_followup(self, followup_id: int) -> Optional[Dict[str, Any]]:
        return self._find("followups", followup_id)

    def complete_followup(self, followup_id: int) -> Dict[str, Any]:
        followup = self._require_followup(followup_id)
        followup["status"] = "completed"
        self.save()
        return followup

    def _require_task(self, task_id: int) -> Dict[str, Any]:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"Task {task_id} not found")
        return task

    def _require_followup(self, followup_id: int) -> Dict[str, Any]:
        followup = self.get_followup(followup_id)
        if followup is None:
            raise KeyError(f"Follow-up {followup_id} not found")
        return followup
