import re

def parse_command(command_str):
    command_str = command_str.strip()
    if not command_str.startswith('/'):
        return None, "Command must start with '/'"
        
    parts = command_str.split(' ', 1)
    cmd = parts[0].lower()
    args_str = parts[1] if len(parts) > 1 else ""
    
    if cmd == "/add":
        if not args_str:
            return None, "Usage: /add <title> [--daily|--weekly|--monthly] [--due YYYY-MM-DD]"
        
        freq = 'once'
        if '--daily' in args_str:
            freq = 'daily'
            args_str = args_str.replace('--daily', '')
        elif '--weekly' in args_str:
            freq = 'weekly'
            args_str = args_str.replace('--weekly', '')
        elif '--monthly' in args_str:
            freq = 'monthly'
            args_str = args_str.replace('--monthly', '')
            
        due_date = None
        due_match = re.search(r'--due\s+(\d{4}-\d{2}-\d{2})', args_str)
        if due_match:
            due_date = due_match.group(1)
            args_str = re.sub(r'--due\s+\d{4}-\d{2}-\d{2}', '', args_str)
            
        title = args_str.strip()
        title = re.sub(r'\s+', ' ', title)
        
        # Remove any stray quotes around title if user added them
        if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
            title = title[1:-1].strip()
            
        if not title:
            return None, "Task title cannot be empty"
        return {"action": "add", "title": title, "frequency": freq, "due_date": due_date}, None
        
    elif cmd == "/done":
        if not args_str:
            return None, "Usage: /done <task_id>"
        try:
            task_id = int(args_str.strip())
            return {"action": "done", "task_id": task_id}, None
        except ValueError:
            return None, "Task ID must be an integer"
            
    elif cmd == "/todo":
        if not args_str:
            return None, "Usage: /todo <task_id>"
        try:
            task_id = int(args_str.strip())
            return {"action": "todo", "task_id": task_id}, None
        except ValueError:
            return None, "Task ID must be an integer"
            
    elif cmd == "/delete":
        if not args_str:
            return None, "Usage: /delete <task_id>"
        try:
            task_id = int(args_str.strip())
            return {"action": "delete", "task_id": task_id}, None
        except ValueError:
            return None, "Task ID must be an integer"
            
    elif cmd == "/journal":
        if not args_str:
            return None, "Usage: /journal <entry_text> [--mood 1-5] [--tags tag1,tag2]"
            
        mood = 3
        mood_match = re.search(r'--mood\s+(\d)', args_str)
        if mood_match:
            mood = int(mood_match.group(1))
            if mood < 1 or mood > 5:
                return None, "Mood score must be between 1 and 5"
            args_str = re.sub(r'--mood\s+\d', '', args_str)
            
        tags = ""
        tags_match = re.search(r'--tags\s+("[^"]*"|\'[^\']*\'|[^\s]+)', args_str)
        if tags_match:
            tags = tags_match.group(1)
            if (tags.startswith('"') and tags.endswith('"')) or (tags.startswith("'") and tags.endswith("'")):
                tags = tags[1:-1].strip()
            args_str = args_str.replace(tags_match.group(0), "")
            
        entry_text = args_str.strip()
        if (entry_text.startswith('"') and entry_text.endswith('"')) or \
           (entry_text.startswith("'") and entry_text.endswith("'")):
            entry_text = entry_text[1:-1].strip()
            
        if not entry_text:
            return None, "Journal entry text cannot be empty"
        return {"action": "journal", "entry_text": entry_text, "mood": mood, "tags": tags}, None
        
    elif cmd == "/help":
        return {"action": "help"}, None
        
    elif cmd == "/clear":
        return {"action": "clear"}, None
        
    else:
        return None, f"Unknown command: {cmd}. Type /help for a list of commands."
