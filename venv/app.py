import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Input, RichLog, TextArea, Button, Label, ListView, ListItem, Static
from textual.containers import Vertical, Horizontal, Container
from textual.binding import Binding

import db
import commands

# CSS stylesheet embedded in the python code for portability
TCSS_CONTENT = """
Screen {
    background: #0d1117;
    color: #c9d1d9;
}

#header-title {
    background: #161b22;
    color: #00ff66;
    text-align: center;
    text-style: bold;
    height: 3;
    content-align: center middle;
    border-bottom: double #30363d;
}

#main-grid {
    layout: grid;
    grid-size: 2 1;
    grid-columns: 13fr 10fr;
    height: 1fr;
}

#left-panel {
    border-right: tall #30363d;
    padding: 1 1 1 1;
}

#right-panel {
    layout: vertical;
    padding: 1 1 1 1;
}

TabbedContent {
    height: 1fr;
}

TabPane {
    padding: 1;
}

/* Tasks Styles */
.task-section-title {
    color: #00ccff;
    text-style: bold;
    margin-top: 1;
    margin-bottom: 0;
}

ListView {
    background: transparent;
    height: auto;
    margin-bottom: 1;
    border: solid #30363d;
}

ListItem {
    padding: 0 1;
    background: transparent;
    color: #c9d1d9;
}

ListItem:hover {
    background: #1f242c;
}

ListItem.--focus {
    background: #30363d;
    color: #00ff66;
    text-style: bold;
}

.task-done {
    color: #8b949e;
    text-style: strike;
}

.task-todo {
    color: #58a6ff;
}

.task-due-date {
    color: #ff7b72;
}

/* Journal Styles */
#journal-form {
    layout: vertical;
}

#journal-label {
    color: #00ccff;
    text-style: bold;
    margin-bottom: 1;
}

#journal-text {
    height: 10;
    border: tall #30363d;
    background: #090c10;
    color: #c9d1d9;
    margin-bottom: 1;
}

#journal-text:focus {
    border: tall #00ccff;
}

.form-row {
    layout: grid;
    grid-size: 2 1;
    grid-columns: 1fr 3fr;
    height: 3;
    align: left middle;
    margin-bottom: 1;
}

.form-label {
    color: #8b949e;
    align-vertical: middle;
}

.form-input {
    background: #090c10;
    border: tall #30363d;
    color: #ffffff;
    height: 3;
}

.form-input:focus {
    border: tall #00ccff;
}

#save-journal-btn {
    background: #14321a;
    color: #00ff66;
    border: tall #00ff66;
    width: 100%;
    text-style: bold;
    margin-top: 1;
}

#save-journal-btn:hover {
    background: #00ff66;
    color: #0d1117;
}

/* Analytics Styles */
#analytics-scroll {
    overflow-y: scroll;
    height: 100%;
}

#analytics-content {
    background: transparent;
    color: #c9d1d9;
    padding: 1;
}

/* Right Panel Styles */
#followup-panel {
    height: 35%;
    border: tall #30363d;
    padding: 1;
    margin-bottom: 1;
    layout: vertical;
}

#followup-title {
    color: #ffcc00;
    text-style: bold;
    margin-bottom: 1;
}

#followup-list {
    background: transparent;
    border: none;
    height: 1fr;
}

.followup-item {
    color: #ffcc00;
}

.followup-good {
    color: #00ff66;
}

#console-panel {
    height: 65%;
    layout: vertical;
}

#console-title {
    color: #00ff66;
    text-style: bold;
    margin-bottom: 1;
}

#console-log {
    height: 1fr;
    background: #090c10;
    border: tall #30363d;
    color: #8b949e;
    padding: 0 1;
}

#console-input {
    background: #090c10;
    border: tall #30363d;
    color: #ffffff;
    height: 3;
}

#console-input:focus {
    border: tall #00ff66;
}
"""

class TaskItem(ListItem):
    def __init__(self, task_id, title, frequency, status, due_date=None):
        super().__init__()
        self.task_id = task_id
        self.task_status = status
        self.title_text = title
        self.frequency = frequency
        self.due_date = due_date

    def compose(self) -> ComposeResult:
        checkbox = "[x]" if self.task_status == 'done' else "[ ]"
        status_class = "task-done" if self.task_status == 'done' else "task-todo"
        
        due_str = ""
        if self.due_date:
            due_str = f" [Due: {self.due_date}]"
            
        yield Label(f"{checkbox} #{self.task_id} - {self.title_text}{due_str}", classes=status_class)

class SuperpowerTerminalApp(App):
    TITLE = "Superpower Terminal"
    CSS = TCSS_CONTENT
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh UI", show=True),
        Binding("c", "focus_console", "Focus CLI", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("⚡ SUPERPOWER TERMINAL v1.0 ⚡", id="header-title")
        
        with Container(id="main-grid"):
            # Left panel with Tabbed Content
            with Vertical(id="left-panel"):
                with TabbedContent():
                    with TabPane("Tasks", id="tab-tasks"):
                        yield Label("▼ DAILY HABITS", classes="task-section-title")
                        yield ListView(id="daily-tasks")
                        
                        yield Label("▼ WEEKLY TASKS", classes="task-section-title")
                        yield ListView(id="weekly-tasks")
                        
                        yield Label("▼ MONTHLY TASKS", classes="task-section-title")
                        yield ListView(id="monthly-tasks")
                        
                        yield Label("▼ ONCE-OFF TASKS", classes="task-section-title")
                        yield ListView(id="once-tasks")
                        
                    with TabPane("Journal", id="tab-journal"):
                        yield Label("Today's Reflection Log", id="journal-label")
                        yield TextArea(placeholder="How was today? What did you achieve? Write your thoughts...", id="journal-text")
                        
                        with Container(classes="form-row"):
                            yield Label("Mood (1-5):", classes="form-label")
                            yield Input(placeholder="e.g. 5 (Awesome) to 1 (Tired)", id="journal-mood", classes="form-input")
                            
                        with Container(classes="form-row"):
                            yield Label("Tags:", classes="form-label")
                            yield Input(placeholder="e.g. work, coding, health", id="journal-tags", classes="form-input")
                            
                        yield Button("Save Daily Log", id="save-journal-btn", variant="success")
                        
                    with TabPane("Analytics", id="tab-analytics"):
                        with Vertical(id="analytics-scroll"):
                            yield Static(id="analytics-content")
            
            # Right panel with Followups & Console
            with Vertical(id="right-panel"):
                with Vertical(id="followup-panel"):
                    yield Label("▼ TASK FOLLOW-UP & ALERTS", id="followup-title")
                    yield ListView(id="followup-list")
                    
                with Vertical(id="console-panel"):
                    yield Label("▼ COMMAND CONSOLE", id="console-title")
                    yield RichLog(id="console-log", max_lines=1000)
                    yield Input(placeholder="Enter command (e.g. /help, /add 'Buy milk' --daily)...", id="console-input")
                    
        yield Footer()

    def on_mount(self) -> None:
        db.init_db()
        self.refresh_ui()
        self.log_message("[green]System initialised successfully.[/green]")
        self.log_message("Type [cyan]/help[/cyan] in the command input below for a list of shortcuts and commands.")
        # Focus on the command line input immediately
        self.query_one("#console-input", Input).focus()

    def action_focus_console(self) -> None:
        self.query_one("#console-input", Input).focus()

    def action_refresh(self) -> None:
        self.refresh_ui()
        self.log_message("[cyan]UI Refreshed.[/cyan]")

    def log_message(self, message: str) -> None:
        console_log = self.query_one("#console-log", RichLog)
        console_log.write(message)

    def refresh_ui(self) -> None:
        self.reload_tasks()
        self.reload_today_journal()
        self.reload_analytics()
        self.reload_followups()

    def reload_tasks(self) -> None:
        tasks = db.get_all_tasks()
        
        daily_list = self.query_one("#daily-tasks", ListView)
        weekly_list = self.query_one("#weekly-tasks", ListView)
        monthly_list = self.query_one("#monthly-tasks", ListView)
        once_list = self.query_one("#once-tasks", ListView)
        
        # Clear existing items
        daily_list.clear()
        weekly_list.clear()
        monthly_list.clear()
        once_list.clear()
        
        for t in tasks:
            item = TaskItem(t['id'], t['title'], t['frequency'], t['status'], t['due_date'])
            if t['frequency'] == 'daily':
                daily_list.append(item)
            elif t['frequency'] == 'weekly':
                weekly_list.append(item)
            elif t['frequency'] == 'monthly':
                monthly_list.append(item)
            else:
                once_list.append(item)

    def reload_today_journal(self) -> None:
        today_entry = db.get_journal_entry_for_today()
        
        text_area = self.query_one("#journal-text", TextArea)
        mood_input = self.query_one("#journal-mood", Input)
        tags_input = self.query_one("#journal-tags", Input)
        
        # Only populate if TextArea is empty (so we don't overwrite user's active typing)
        if today_entry and not text_area.text:
            text_area.text = today_entry['entry_text']
            mood_input.value = str(today_entry['mood_score'])
            tags_input.value = today_entry['tags'] or ""

    def reload_analytics(self) -> None:
        data = db.get_analytics()
        analytics_panel = self.query_one("#analytics-content", Static)
        
        todo = data.get('todo_count', 0)
        done = data.get('done_count', 0)
        total = todo + done
        rate = int((done / total) * 100) if total > 0 else 0
        
        # Progress bar
        bar_width = 16
        filled = int(rate / 100 * bar_width) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        
        content = f"[magenta]■ TASK COMPLETION STATUS[/magenta]\n"
        content += f"Progress: [{bar}] {rate}% ({done}/{total} completed)\n\n"
        
        # Frequency breakdown
        content += "[magenta]■ COMPLETION BY FREQUENCY[/magenta]\n"
        fb = data.get('frequency_breakdown', {})
        for freq in ['daily', 'weekly', 'monthly', 'once']:
            f_todo = fb.get(freq, {}).get('todo', 0)
            f_done = fb.get(freq, {}).get('done', 0)
            f_total = f_todo + f_done
            f_rate = int((f_done / f_total) * 100) if f_total > 0 else 0
            f_bar = "█" * int(f_rate/10) + "░" * (10 - int(f_rate/10))
            content += f"  {freq.capitalize():8} [{f_bar}] {f_rate}% ({f_done}/{f_total})\n"
            
        content += "\n"
        
        # Journal Streak
        streak = data.get('journal_streak', 0)
        streak_fire = "🔥" * min(5, streak) if streak > 0 else "❄️"
        content += f"[magenta]■ REFLECTION STREAK[/magenta]\n"
        content += f"  Streak: {streak} Days {streak_fire}\n\n"
        
        # Mood History Chart (Sparkline)
        content += "[magenta]■ MOOD HISTORY (LAST 7 ENTRIES)[/magenta]\n"
        moods = data.get('mood_history', [])
        if moods:
            max_mood = 5
            for score in range(max_mood, 0, -1):
                line = f"  {score} |"
                for date_str, mood in moods:
                    if mood >= score:
                        line += "  █  "
                    else:
                        line += "     "
                content += line + "\n"
            
            dates_line = "     +" + "-----" * len(moods) + "\n"
            dates_line += "      "
            for date_str, _ in moods:
                # show MM-DD
                dates_line += f" {date_str[5:]} "
            content += dates_line + "\n"
        else:
            content += "  No journal entries recorded yet.\n"
            
        content += "\n"
        
        # Top tags
        content += "[magenta]■ TOP REFLECTION TAGS[/magenta]\n"
        tags = data.get('top_tags', [])
        if tags:
            tag_str = ", ".join([f"#{t} ({c})" for t, c in tags])
            content += f"  {tag_str}\n"
        else:
            content += "  No tags recorded yet.\n"
            
        analytics_panel.update(content)

    def reload_followups(self) -> None:
        followup_list = self.query_one("#followup-list", ListView)
        followup_list.clear()
        
        today = datetime.date.today()
        tasks = db.get_all_tasks()
        
        count = 0
        for t in tasks:
            if t['status'] == 'todo':
                reason = None
                if t['due_date']:
                    due = db.parse_date(t['due_date'])
                    if due and due < today:
                        reason = f"Overdue since {t['due_date']}"
                else:
                    created_date_str = t['created_at'].split(' ')[0]
                    created_date = db.parse_date(created_date_str)
                    if created_date and (today - created_date).days >= 3 and t['frequency'] == 'once':
                        reason = f"Stale (Created {(today - created_date).days}d ago)"
                
                if reason:
                    count += 1
                    item = TaskItem(t['id'], t['title'], t['frequency'], t['status'], t['due_date'])
                    # Wrap label in item with warning class
                    item.task_id = t['id']
                    item.task_status = t['status']
                    followup_list.append(item)
                    
        if count == 0:
            followup_list.append(ListItem(Label("✅ All tasks on track!", classes="followup-good")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        # Enter key or Click on a Task toggles its status
        item = event.item
        if item and hasattr(item, 'task_id'):
            task_id = item.task_id
            current_status = item.task_status
            
            if current_status == 'todo':
                db.complete_task(task_id)
                self.log_message(f"[green]✓ Completed task #{task_id}[/green]")
            else:
                db.uncomplete_task(task_id)
                self.log_message(f"[yellow]↩ Marked task #{task_id} as TODO[/yellow]")
                
            self.refresh_ui()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-journal-btn":
            text_area = self.query_one("#journal-text", TextArea)
            mood_input = self.query_one("#journal-mood", Input)
            tags_input = self.query_one("#journal-tags", Input)
            
            text = text_area.text.strip()
            mood_str = mood_input.value.strip()
            tags = tags_input.value.strip()
            
            if not text:
                self.log_message("[red]Error: Journal text cannot be empty.[/red]")
                return
                
            try:
                mood = int(mood_str) if mood_str else 3
                if mood < 1 or mood > 5:
                    raise ValueError()
            except ValueError:
                self.log_message("[red]Error: Mood must be an integer between 1 and 5.[/red]")
                return
                
            db.save_journal_entry(text, mood, tags)
            self.log_message(f"[green]✓ Saved daily journal. Mood: {mood}/5[/green]")
            self.refresh_ui()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "console-input":
            cmd = event.value
            if cmd:
                self.handle_command(cmd)
                event.input.value = ""

    def handle_command(self, cmd_text: str) -> None:
        res, err = commands.parse_command(cmd_text)
        if err:
            self.log_message(f"[red]Error: {err}[/red]")
            return
            
        action = res["action"]
        if action == "add":
            task_id = db.add_task(res["title"], res["frequency"], res["due_date"])
            freq_str = f" ({res['frequency']})" if res['frequency'] != 'once' else ""
            due_str = f" due {res['due_date']}" if res['due_date'] else ""
            self.log_message(f"[green]✓ Added task #{task_id}: {res['title']}{freq_str}{due_str}[/green]")
            self.refresh_ui()
            
        elif action == "done":
            db.complete_task(res["task_id"])
            self.log_message(f"[green]✓ Completed task #{res['task_id']}[/green]")
            self.refresh_ui()
            
        elif action == "todo":
            db.uncomplete_task(res["task_id"])
            self.log_message(f"[yellow]↩ Task #{res['task_id']} marked as TODO[/yellow]")
            self.refresh_ui()
            
        elif action == "delete":
            db.delete_task(res["task_id"])
            self.log_message(f"[red]✗ Deleted task #{res['task_id']}[/red]")
            self.refresh_ui()
            
        elif action == "journal":
            db.save_journal_entry(res["entry_text"], res["mood"], res["tags"])
            self.log_message(f"[green]✓ Saved daily reflection. Mood: {res['mood']}/5[/green]")
            self.refresh_ui()
            
        elif action == "help":
            self.log_message("[yellow]Available Commands:[/yellow]")
            self.log_message("  [cyan]/add <title>[/cyan] - Add a task (e.g. [italic]/add Buy milk[/italic])")
            self.log_message("  [cyan]/add <title> --daily[/cyan] - Add daily repeating task")
            self.log_message("  [cyan]/add <title> --weekly[/cyan] - Add weekly repeating task")
            self.log_message("  [cyan]/add <title> --monthly[/cyan] - Add monthly repeating task")
            self.log_message("  [cyan]/add <title> --due YYYY-MM-DD[/cyan] - Add task with due date")
            self.log_message("  [cyan]/done <task_id>[/cyan] - Complete a task")
            self.log_message("  [cyan]/todo <task_id>[/cyan] - Uncomplete a task")
            self.log_message("  [cyan]/delete <task_id>[/cyan] - Delete a task")
            self.log_message("  [cyan]/journal \"entry\" --mood 1-5 --tags \"tag1,tag2\"[/cyan] - Log daily journal")
            self.log_message("  [cyan]/clear[/cyan] - Clear console log")
            
        elif action == "clear":
            self.query_one("#console-log", RichLog).clear()

if __name__ == "__main__":
    app = SuperpowerTerminalApp()
    app.run()
