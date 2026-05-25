# Superpower Terminal Todo

A terminal-first productivity app with todo management, recurring schedules, journaling, and follow-up workflows.

## Install

Use Python 3.11 or newer.

```bash
python -m pip install -e .
```

## Terminal Usage

Run the app directly from the terminal with Python, or use the package entrypoint after installation.

```bash
python superpower_todo.py task add "Plan sprint" --description "Define next steps" --due 2026-05-25 --recurrence weekly
python superpower_todo.py task list
python superpower_todo.py task show 1
```

If installed in editable mode, you can also use the command directly as:

```bash
superpower-todo task list
```

## Unified Workflow UI

Use the `ui` command to review the current workflow in one consolidated terminal view.

```bash
python superpower_todo.py ui
python superpower_todo.py ui --days 5
python superpower_todo.py ui --task 1
python superpower_todo.py ui --journal 1
python superpower_todo.py ui --followup 1
```

## Run

```bash
python superpower_todo.py task add "Plan sprint" --description "Define next steps" --due 2026-05-25 --recurrence weekly
python superpower_todo.py task list
python superpower_todo.py task show 1
```

## Journal

```bash
python superpower_todo.py journal add "Daily reflection" --content "Reviewed progress" --task 1
python superpower_todo.py journal list
python superpower_todo.py journal show 1
```

## Follow-up

```bash
python superpower_todo.py followup add 1 --note "Review after task completion" --due 2026-06-01
python superpower_todo.py followup list --task 1
python superpower_todo.py followup complete 1
```

## Storage

Data is stored locally in `~/.config/superpower-terminal-todo/data.json`.
