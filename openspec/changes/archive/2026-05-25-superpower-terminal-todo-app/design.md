## Context

This change introduces a terminal-native productivity app that integrates todo management, recurring schedules, journaling, and task follow-up. It is intended for users who prefer working in the terminal and need a unified workflow for planning, reflection, and progress tracking.

## Goals / Non-Goals

**Goals:**
- Provide a CLI-first task manager with support for recurring scheduling.
- Add journal entry capabilities that are accessible from the terminal.
- Offer follow-up workflows for reminders, status reviews, and next-step planning.
- Keep the initial implementation modular so features can be extended independently.

**Non-Goals:**
- Not building a full graphical UI or web interface in this change.
- Not integrating with external calendar services or third-party task sync providers initially.
- Not implementing heavyweight analytics or AI-based task recommendations in the first version.

## Decisions

- Use a single terminal application binary or script with subcommands for tasks, recurring schedules, journal entries, and follow-up actions. This keeps the UX consistent and minimizes scope.
- Store data in a local file-based datastore (e.g. JSON, YAML, or SQLite) to simplify the first implementation and support offline terminal usage.
- Model recurring tasks separately from one-off todos, with recurrence metadata attached to each task for schedule generation and completion tracking.
- Use journal entries as first-class objects that can optionally reference task IDs, enabling reflections that are linked to relevant todo work without requiring a separate external system.
- Expose task follow-up operations as explicit commands for reminders and review history, so users can retrieve follow-up context without manual label searching.

## Risks / Trade-offs

- [Risk] Local storage could limit collaboration if a later version needs cloud sync. → Mitigation: design the data model with clear boundaries so storage can be replaced or extended later.
- [Risk] Recurring schedule complexity can grow quickly with custom rules. → Mitigation: start with daily/weekly/monthly patterns and add custom recurrence only after core functionality is stable.
- [Risk] Terminal UX can be hard to learn if commands are too verbose. → Mitigation: provide sensible defaults, help text, and concise command aliases.

## Migration Plan

- Implement the app in a new module or command namespace to avoid conflicts with existing terminal tooling.
- Validate the data model with sample tasks, recurring entries, and journal notes.
- If existing workspace state storage already exists, migrate only if data shape is compatible; otherwise keep the new app isolated.

## Open Questions

- Should the journal component support tags or just date-based retrieval in the first version?
- Will follow-up reminders be scheduled relative to task completion, or based on explicit review dates provided by the user?
