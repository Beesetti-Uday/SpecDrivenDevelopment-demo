import sqlite3
import datetime
import os

DB_NAME = "db.sqlite3"

def get_db_path():
    # Store database in the same directory as this script
    dir_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_path, DB_NAME)

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        frequency TEXT NOT NULL, -- 'once', 'daily', 'weekly', 'monthly'
        status TEXT NOT NULL DEFAULT 'todo', -- 'todo', 'done'
        due_date TEXT, -- YYYY-MM-DD
        last_completed TEXT, -- YYYY-MM-DD
        created_at TEXT NOT NULL
    )
    """)
    
    # Create journal table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_text TEXT NOT NULL,
        mood_score INTEGER NOT NULL, -- 1 to 5
        tags TEXT, -- comma-separated list of tags
        created_date TEXT NOT NULL UNIQUE, -- YYYY-MM-DD (one entry per day maximum)
        created_at TEXT NOT NULL
    )
    """)
    
    # Check if we should insert sample data
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sample_tasks = [
            ("Morning meditation & stretching", "daily", "done", today_str, now_str),
            ("Read 15 pages of a book", "daily", "todo", None, now_str),
            ("Plan the upcoming week", "weekly", "todo", None, now_str),
            ("Review monthly financial goals", "monthly", "todo", None, now_str),
            ("Explore this Superpower Terminal App!", "once", "todo", None, now_str),
            ("Stale task that needs follow-up", "once", "todo", None, (datetime.date.today() - datetime.timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, frequency, status, last_completed, created_at) VALUES (?, ?, ?, ?, ?)",
            sample_tasks
        )
        
        # Populate journal entries for the last 5 days to feed analytics
        for i in range(5, 0, -1):
            date_val = datetime.date.today() - datetime.timedelta(days=i)
            date_str = date_val.strftime("%Y-%m-%d")
            entry = f"Reflection log for {date_str}. Focused on terminal workspace design."
            mood = 3 + (i % 3)
            tags = "work,coding,design" if i % 2 == 0 else "health,fitness"
            cursor.execute(
                "INSERT OR IGNORE INTO journal (entry_text, mood_score, tags, created_date, created_at) VALUES (?, ?, ?, ?, ?)",
                (entry, mood, tags, date_str, date_str + " 12:00:00")
            )
            
    conn.commit()
    conn.close()

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def needs_rollover(frequency, last_completed_str, current_date=None):
    if not last_completed_str:
        return False
    
    last_completed = parse_date(last_completed_str)
    if not last_completed:
        return False
    
    if not current_date:
        current_date = datetime.date.today()
        
    if frequency == 'daily':
        return current_date > last_completed
    elif frequency == 'weekly':
        curr_yr, curr_wk, _ = current_date.isocalendar()
        last_yr, last_wk, _ = last_completed.isocalendar()
        return (curr_yr, curr_wk) != (last_yr, last_wk)
    elif frequency == 'monthly':
        return (current_date.year, current_date.month) != (last_completed.year, last_completed.month)
    return False

def check_and_apply_rollovers():
    """Runs through completed recurring tasks and resets them if their frequency window has rolled over."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, frequency, last_completed FROM tasks WHERE status = 'done' AND frequency != 'once'")
    completed_tasks = cursor.fetchall()
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    rolled_over_ids = []
    
    for task_id, title, freq, last_completed in completed_tasks:
        if needs_rollover(freq, last_completed):
            rolled_over_ids.append(task_id)
            
    if rolled_over_ids:
        # Reset task status to 'todo'
        cursor.execute(
            f"UPDATE tasks SET status = 'todo' WHERE id IN ({','.join('?' for _ in rolled_over_ids)})",
            rolled_over_ids
        )
        conn.commit()
        
    conn.close()
    return len(rolled_over_ids)

def add_task(title, frequency, due_date=None):
    if frequency not in ('once', 'daily', 'weekly', 'monthly'):
        raise ValueError("Invalid frequency. Must be 'once', 'daily', 'weekly', or 'monthly'.")
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO tasks (title, frequency, status, due_date, created_at) VALUES (?, ?, 'todo', ?, ?)",
        (title, frequency, due_date, now_str)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def complete_task(task_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute(
        "UPDATE tasks SET status = 'done', last_completed = ? WHERE id = ?",
        (today_str, task_id)
    )
    conn.commit()
    conn.close()

def uncomplete_task(task_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE tasks SET status = 'todo', last_completed = NULL WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

def delete_task(task_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_all_tasks():
    # Always check rollovers first
    check_and_apply_rollovers()
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks ORDER BY status DESC, frequency, id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_journal_entry(entry_text, mood_score, tags_str=""):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Clean tags
    tags_list = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
    cleaned_tags = ",".join(tags_list)
    
    cursor.execute(
        """
        INSERT INTO journal (entry_text, mood_score, tags, created_date, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(created_date) DO UPDATE SET
            entry_text = excluded.entry_text,
            mood_score = excluded.mood_score,
            tags = excluded.tags,
            created_at = excluded.created_at
        """,
        (entry_text, mood_score, cleaned_tags, today_str, now_str)
    )
    conn.commit()
    conn.close()

def get_journal_entries(limit=10):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM journal ORDER BY created_date DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_journal_entry_for_today():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM journal WHERE created_date = ?", (today_str,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_analytics():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    analytics = {}
    
    # 1. Total tasks completed vs pending
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    status_counts = dict(cursor.fetchall())
    analytics['todo_count'] = status_counts.get('todo', 0)
    analytics['done_count'] = status_counts.get('done', 0)
    
    # 2. Tasks completion rate by frequency
    cursor.execute("SELECT frequency, status, COUNT(*) FROM tasks GROUP BY frequency, status")
    freq_data = cursor.fetchall()
    freq_rates = {}
    for freq, status, count in freq_data:
        if freq not in freq_rates:
            freq_rates[freq] = {'todo': 0, 'done': 0}
        freq_rates[freq][status] = count
    analytics['frequency_breakdown'] = freq_rates
    
    # 3. Mood history (last 7 entries)
    cursor.execute("SELECT created_date, mood_score FROM journal ORDER BY created_date DESC LIMIT 7")
    mood_history = cursor.fetchall()
    analytics['mood_history'] = list(reversed(mood_history)) # chronologically
    
    # 4. Top Tags
    cursor.execute("SELECT tags FROM journal WHERE tags IS NOT NULL AND tags != ''")
    all_tags_rows = cursor.fetchall()
    tag_counts = {}
    for (tags_str,) in all_tags_rows:
        for t in tags_str.split(","):
            t = t.strip()
            if t:
                tag_counts[t] = tag_counts.get(t, 0) + 1
    # Sort tags by count desc
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    analytics['top_tags'] = sorted_tags[:5]
    
    # 5. Daily completed task streaks
    # To compute daily streak: check how many consecutive days (going backwards from today) 
    # the user has written a journal entry OR completed a task.
    # Let's check journal entry consecutive days for simplicity and accuracy.
    cursor.execute("SELECT created_date FROM journal ORDER BY created_date DESC")
    dates = [datetime.datetime.strptime(d[0], "%Y-%m-%d").date() for d in cursor.fetchall()]
    
    streak = 0
    if dates:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        # Check if they have an entry for today or yesterday to start the streak
        if dates[0] == today or dates[0] == yesterday:
            streak = 1
            expected = dates[0] - datetime.timedelta(days=1)
            for d in dates[1:]:
                if d == expected:
                    streak += 1
                    expected = d - datetime.timedelta(days=1)
                elif d > expected:
                    continue # Skip duplicates if any
                else:
                    break # Gap in the streak
    analytics['journal_streak'] = streak
    
    conn.close()
    return analytics
