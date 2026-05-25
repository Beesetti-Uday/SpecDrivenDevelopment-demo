from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from terminal_todo.storage import Storage, VALID_RECURRENCES


def format_task(task: dict[str, Any]) -> str:
    recurrence = f" (recurs {task['recurrence']})" if task.get("recurrence") else ""
    due = f" due {task['due_date']}" if task.get("due_date") else ""
    status = task.get("status", "pending")
    return f"[{status}] {task['id']}: {task['title']}{due}{recurrence}"


def print_task_detail(task: dict[str, Any]) -> None:
    print(format_task(task))
    print(f"Description: {task.get('description', '')}")
    if task.get("journal_ids"):
        print(f"Journal IDs: {', '.join(str(i) for i in task['journal_ids'])}")
    if task.get("follow_up_ids"):
        print(f"Follow-up IDs: {', '.join(str(i) for i in task['follow_up_ids'])}")
    if task.get("last_completed"):
        print(f"Last completed: {task['last_completed']}")


def print_journal_detail(journal: dict[str, Any]) -> None:
    print(f"Journal {journal['id']}: {journal['title']}")
    print(f"Date: {journal['date']}")
    if journal.get("task_id") is not None:
        print(f"Linked task: {journal['task_id']}")
    print(journal.get("content", ""))


def print_followup_detail(followup: dict[str, Any]) -> None:
    print(f"Follow-up {followup['id']} for task {followup['task_id']}")
    print(f"Status: {followup['status']}")
    if followup.get("due_date"):
        print(f"Due: {followup['due_date']}")
    print(followup.get("note", ""))


def print_dashboard(summary: dict[str, Any]) -> None:
    print("=== Workflow Review Dashboard ===")
    print("\nPending Tasks:")
    for task in summary["pending_tasks"]:
        print(f"  - {format_task(task)}")
    print("\nDue Soon:")
    for task in summary["due_soon"]:
        print(f"  - {format_task(task)}")
    print("\nRecurring Tasks:")
    for task in summary["recurring_tasks"]:
        print(f"  - {format_task(task)}")
    print("\nRecent Journals:")
    for journal in summary["recent_journals"]:
        print(f"  - {journal['id']}: {journal['title']} ({journal['date']})")
    print("\nPending Follow-ups:")
    for followup in summary["pending_followups"]:
        status = followup.get("status", "pending")
        due = f" due {followup['due_date']}" if followup.get("due_date") else ""
        print(f"  - [{status}] {followup['id']} for task {followup['task_id']}{due}: {followup['note']}")


def print_task_context(storage: Storage, task_id: int) -> None:
    context = storage.task_context(task_id)
    task = context["task"]
    print("=== Task Context ===")
    print_task_detail(task)
    if context["journals"]:
        print("\nLinked Journals:")
        for journal in context["journals"]:
            print(f"  - {journal['id']}: {journal['title']} ({journal['date']})")
    if context["followups"]:
        print("\nPending Follow-ups:")
        for followup in context["followups"]:
            due = f" due {followup['due_date']}" if followup.get("due_date") else ""
            print(f"  - {followup['id']}{due}: {followup['note']}")


def create_task_parser(subparsers: argparse._SubParsersAction) -> None:
    task_parser = subparsers.add_parser("task", help="Manage todos")
    task_subparsers = task_parser.add_subparsers(dest="task_command")

    add_parser = task_subparsers.add_parser("add", help="Create a new todo")
    add_parser.add_argument("title")
    add_parser.add_argument("--description", default="", help="Task description")
    add_parser.add_argument("--due", dest="due_date", help="Due date in YYYY-MM-DD")
    add_parser.add_argument("--recurrence", choices=sorted(VALID_RECURRENCES), help="Recurrence pattern")

    update_parser = task_subparsers.add_parser("update", help="Update an existing todo")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("--title")
    update_parser.add_argument("--description")
    update_parser.add_argument("--due", dest="due_date")
    update_parser.add_argument("--recurrence", choices=sorted(VALID_RECURRENCES))

    complete_parser = task_subparsers.add_parser("complete", help="Complete a todo")
    complete_parser.add_argument("id", type=int)

    delete_parser = task_subparsers.add_parser("delete", help="Delete a todo")
    delete_parser.add_argument("id", type=int)

    list_parser = task_subparsers.add_parser("list", help="List todos")
    list_parser.add_argument("--all", action="store_true", help="Include completed tasks")

    show_parser = task_subparsers.add_parser("show", help="Show a todo detail")
    show_parser.add_argument("id", type=int)


def create_journal_parser(subparsers: argparse._SubParsersAction) -> None:
    journal_parser = subparsers.add_parser("journal", help="Manage journal entries")
    journal_subparsers = journal_parser.add_subparsers(dest="journal_command")

    add_parser = journal_subparsers.add_parser("add", help="Create a journal entry")
    add_parser.add_argument("title")
    add_parser.add_argument("--content", required=True)
    add_parser.add_argument("--task", dest="task_id", type=int, help="Link journal to a task")

    list_parser = journal_subparsers.add_parser("list", help="List journal entries")

    show_parser = journal_subparsers.add_parser("show", help="Show a journal entry")
    show_parser.add_argument("id", type=int)


def create_followup_parser(subparsers: argparse._SubParsersAction) -> None:
    followup_parser = subparsers.add_parser("followup", help="Manage follow-up notes")
    followup_subparsers = followup_parser.add_subparsers(dest="followup_command")

    add_parser = followup_subparsers.add_parser("add", help="Add a follow-up reminder")
    add_parser.add_argument("task_id", type=int)
    add_parser.add_argument("--note", required=True)
    add_parser.add_argument("--due", dest="due_date", help="Due date in YYYY-MM-DD")

    list_parser = followup_subparsers.add_parser("list", help="List follow-ups")
    list_parser.add_argument("--task", dest="task_id", type=int, help="Filter follow-ups by task")

    complete_parser = followup_subparsers.add_parser("complete", help="Complete a follow-up")
    complete_parser.add_argument("id", type=int)


def create_ui_parser(subparsers: argparse._SubParsersAction) -> None:
    ui_parser = subparsers.add_parser("ui", help="Unified workflow review UI")
    ui_parser.add_argument("--task", dest="task_id", type=int, help="Show detailed task context")
    ui_parser.add_argument("--journal", dest="journal_id", type=int, help="Show detailed journal entry")
    ui_parser.add_argument("--followup", dest="followup_id", type=int, help="Show detailed follow-up entry")
    ui_parser.add_argument("--days", dest="days", type=int, default=3, help="How many days ahead to show due items")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser("superpower-todo")
    subparsers = parser.add_subparsers(dest="command")
    create_task_parser(subparsers)
    create_journal_parser(subparsers)
    create_followup_parser(subparsers)
    create_ui_parser(subparsers)
    args = parser.parse_args(argv)
    storage = Storage()

    if args.command == "task":
        if args.task_command == "add":
            task = storage.add_task(args.title, args.description, args.due_date, args.recurrence)
            print(f"Created todo {task['id']}")
        elif args.task_command == "update":
            task = storage.update_task(args.id, args.title, args.description, args.due_date, args.recurrence)
            print_task_detail(task)
        elif args.task_command == "complete":
            task = storage.complete_task(args.id)
            print(f"Completed todo {task['id']}")
        elif args.task_command == "delete":
            storage.delete_task(args.id)
            print(f"Deleted todo {args.id}")
        elif args.task_command == "list":
            for task in storage.list_tasks(include_completed=args.all):
                print(format_task(task))
        elif args.task_command == "show":
            task = storage.get_task(args.id)
            if not task:
                raise SystemExit(f"Task {args.id} not found")
            print_task_detail(task)
        else:
            parser.print_help()
    elif args.command == "journal":
        if args.journal_command == "add":
            journal = storage.add_journal(args.title, args.content, args.task_id)
            print(f"Created journal entry {journal['id']}")
        elif args.journal_command == "list":
            for journal in storage.list_journals():
                print(f"{journal['id']}: {journal['title']} ({journal['date']})")
        elif args.journal_command == "show":
            journal = storage.get_journal(args.id)
            if not journal:
                raise SystemExit(f"Journal {args.id} not found")
            print_journal_detail(journal)
        else:
            parser.print_help()
    elif args.command == "followup":
        if args.followup_command == "add":
            followup = storage.add_followup(args.task_id, args.note, args.due_date)
            print(f"Created follow-up {followup['id']} for task {followup['task_id']}")
        elif args.followup_command == "list":
            for followup in storage.list_followups(task_id=args.task_id):
                print_followup_detail(followup)
                print("---")
        elif args.followup_command == "complete":
            followup = storage.complete_followup(args.id)
            print(f"Completed follow-up {followup['id']}")
        else:
            parser.print_help()
    elif args.command == "ui":
        if args.task_id is not None:
            print_task_context(storage, args.task_id)
        elif args.journal_id is not None:
            journal = storage.get_journal(args.journal_id)
            if not journal:
                raise SystemExit(f"Journal {args.journal_id} not found")
            print_journal_detail(journal)
        elif args.followup_id is not None:
            followup = storage.get_followup(args.followup_id)
            if not followup:
                raise SystemExit(f"Follow-up {args.followup_id} not found")
            print_followup_detail(followup)
        else:
            print_dashboard(storage.dashboard_summary(upcoming_days=args.days))
    else:
        parser.print_help()
