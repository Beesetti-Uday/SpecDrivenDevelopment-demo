import unittest
from commands import parse_command

class TestCommands(unittest.TestCase):
    def test_add_commands(self):
        # Basic add
        res, err = parse_command("/add Read a book")
        self.assertIsNone(err)
        self.assertEqual(res["action"], "add")
        self.assertEqual(res["title"], "Read a book")
        self.assertEqual(res["frequency"], "once")
        self.assertIsNone(res["due_date"])
        
        # Add with frequency flag
        res, err = parse_command("/add Do pushups --daily")
        self.assertIsNone(err)
        self.assertEqual(res["title"], "Do pushups")
        self.assertEqual(res["frequency"], "daily")
        
        # Add with due date
        res, err = parse_command("/add Submit homework --due 2026-06-01")
        self.assertIsNone(err)
        self.assertEqual(res["title"], "Submit homework")
        self.assertEqual(res["due_date"], "2026-06-01")
        self.assertEqual(res["frequency"], "once")

    def test_done_todo_delete(self):
        res, err = parse_command("/done 42")
        self.assertIsNone(err)
        self.assertEqual(res, {"action": "done", "task_id": 42})
        
        res, err = parse_command("/todo abc")
        self.assertEqual(err, "Task ID must be an integer")
        
        res, err = parse_command("/delete")
        self.assertEqual(err, "Usage: /delete <task_id>")

    def test_journal(self):
        res, err = parse_command('/journal "Reflecting on a great day" --mood 5 --tags "happy,productive"')
        self.assertIsNone(err)
        self.assertEqual(res["action"], "journal")
        self.assertEqual(res["entry_text"], "Reflecting on a great day")
        self.assertEqual(res["mood"], 5)
        self.assertEqual(res["tags"], "happy,productive")

    def test_general_commands(self):
        res, err = parse_command("/help")
        self.assertIsNone(err)
        self.assertEqual(res, {"action": "help"})

if __name__ == '__main__':
    unittest.main()
