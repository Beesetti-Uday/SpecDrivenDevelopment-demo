import tempfile
import unittest
from pathlib import Path

from terminal_todo.storage import Storage


class TerminalTodoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "data.json"
        self.storage = Storage(self.data_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_task_creation_and_completion(self) -> None:
        task = self.storage.add_task("Write plan", "Initial planning", "2026-05-25", "weekly")
        self.assertEqual(task["status"], "pending")
        self.assertEqual(task["recurrence"], "weekly")

        completed = self.storage.complete_task(task["id"])
        self.assertEqual(completed["status"], "pending")
        self.assertEqual(completed["last_completed"], completed["last_completed"])
        self.assertNotEqual(completed["due_date"], "2026-05-25")

    def test_journal_linked_to_task(self) -> None:
        task = self.storage.add_task("Prepare notes", "Write journal prompt")
        journal = self.storage.add_journal("Daily reflection", "Today went well", task["id"])
        self.assertEqual(journal["task_id"], task["id"])
        self.assertIn(journal["id"], self.storage.get_task(task["id"])["journal_ids"])

    def test_followup_creation_and_completion(self) -> None:
        task = self.storage.add_task("Review progress", "Follow-up on weekly goals")
        followup = self.storage.add_followup(task["id"], "Check results next week", "2026-06-01")
        self.assertEqual(followup["task_id"], task["id"])
        self.assertEqual(followup["status"], "pending")

        completed = self.storage.complete_followup(followup["id"])
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(self.storage.get_followup(followup["id"])["status"], "completed")

    def test_task_listing_includes_recurring(self) -> None:
        recurring = self.storage.add_task("Daily review", "Review journal", "2026-05-25", "daily")
        self.storage.complete_task(recurring["id"])
        tasks = self.storage.list_tasks()
        self.assertTrue(any(task["id"] == recurring["id"] for task in tasks))

    def test_dashboard_summary_and_task_context(self) -> None:
        task = self.storage.add_task("Prepare weekly summary", "Review work", "2026-05-25", "weekly")
        self.storage.add_journal("Weekly reflection", "Reviewed progress", task["id"])
        self.storage.add_followup(task["id"], "Check next action", "2026-05-27")
        summary = self.storage.dashboard_summary(upcoming_days=7)
        self.assertTrue(any(item["id"] == task["id"] for item in summary["pending_tasks"]))
        self.assertTrue(any(item["task_id"] == task["id"] for item in summary["pending_followups"]))
        context = self.storage.task_context(task["id"])
        self.assertEqual(context["task"]["id"], task["id"])
        self.assertEqual(len(context["journals"]), 1)
        self.assertEqual(len(context["followups"]), 1)


if __name__ == "__main__":
    unittest.main()
