# ⚡ Superpower Terminal App (TUI) ⚡

A premium, keyboard-driven Terminal User Interface (TUI) application designed for habit tracking, repeating todo lists, personal journaling, and self-reflection analytics.

```text
  ___  _   _ ___  _____ ____  _____   _____ ____  __  __
 / __|| | | | _ \|  ___|  _ \|  _  \ /  _  \  _ \|  \/  |
 \__ \| |_| |  _/|  __||  _ <| |_| | | |_| |  __/| |\/| |
 |___/\_____|_|  |_____|_| \_\_____/ \_____|_|   |_|  |_|
```

## Features

1. **Repeating Todo List**:
   - Supports daily, weekly, monthly, and one-off tasks.
   - Automatically rolls over and resets completed recurring tasks once their time window passes.
   - Completed items are visually struck out.
2. **Journal of Me (Self-Understanding)**:
   - Form-based journal log for daily reflections, mood scoring (1 to 5), and tagging.
   - Saves daily logs in a local database.
3. **Stale Task Follow-up**:
   - Automatic warning panel highlighting overdue tasks (due date in the past) or stale tasks (created more than 3 days ago but never completed).
4. **Command Console CLI**:
   - Integrated command line inside the application to operate the entire dashboard rapidly using commands.
5. **Visual Text-Based Analytics**:
   - Live analytics tab graphing mood scores over the last 7 entries with ASCII bar charts.
   - Displays completion progress bars and streak metrics.

---

## Installation & Setup

Ensure you have Python 3.10+ installed.

1. **Setup the Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

---

## Command Console CLI Reference

Typing command strings in the **Command Console** input at the bottom right allows you to perform any database operation:

| Command | Description | Example |
|---|---|---|
| `/add <title>` | Add a one-off task | `/add Finish report` |
| `/add <title> --daily` | Add a daily recurring habit | `/add Morning stretch --daily` |
| `/add <title> --weekly` | Add a weekly recurring task | `/add Clean apartment --weekly` |
| `/add <title> --monthly` | Add a monthly recurring task | `/add Pay utility bills --monthly` |
| `/add <title> --due <YYYY-MM-DD>` | Add a task with a due date | `/add Send invoice --due 2026-06-01` |
| `/done <task_id>` | Mark a task as completed | `/done 3` |
| `/todo <task_id>` | Mark a task as incomplete | `/todo 3` |
| `/delete <task_id>` | Delete a task | `/delete 5` |
| `/journal "<text>" --mood <1-5> --tags "<comma_tags>"` | Log today's reflection | `/journal "Feeling highly productive" --mood 5 --tags "coding,focus"` |
| `/clear` | Clear the console history | `/clear` |
| `/help` | Print help instructions | `/help` |

*Note: You can also toggle task completion by selecting them in the list view panels and pressing **Enter**.*

---

## Keyboard Shortcuts

- **`q`**: Quit the application.
- **`r`**: Refresh UI elements manually.
- **`c`**: Focus command console input bar.
- **`Tab` / `Shift+Tab`**: Cycle focus between task lists, tabs, and input forms.
- **`Enter`**: Complete or uncomplete the highlighted task in the list panels.
