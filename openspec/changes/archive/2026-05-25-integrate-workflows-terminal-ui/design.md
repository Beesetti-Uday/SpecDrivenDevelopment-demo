## Context

This change adds an integrated terminal UI layer on top of the existing task, recurring schedule, journal, and follow-up workflows. The goal is to unify these experiences so users can view, navigate, and act on related work items from a single terminal interface.

## Goals / Non-Goals

**Goals:**
- Provide a unified terminal entrypoint and dashboard for workflows.
- Link related tasks, journal notes, recurring schedules, and follow-up actions.
- Keep the unified UI lightweight and terminal-native without adding a graphical interface.

**Non-Goals:**
- Not building a full TUI library or graphical dashboard in this change.
- Not integrating external calendar or note services.
- Not rearchitecting existing storage beyond adding workflow relationships where needed.

## Decisions

- Use a single terminal command namespace for the unified interface, e.g. `superpower-todo ui` or `superpower-todo review`, to avoid branching separate workflow commands.
- Implement the review dashboard as a summarizing command output rather than a live interactive TUI, to reduce complexity and keep the experience compatible with terminals.
- Model workflow relationships explicitly by linking journal entries and follow-ups to tasks, while preserving the existing task and recurrence structures.
- Keep data storage local and file-based, extending the existing task/journal/follow-up model with summary metadata rather than introducing database dependencies.

## Risks / Trade-offs

- [Risk] Merging workflows into one interface could make commands harder to discover. → Mitigation: provide clear dashboard output and help text for the unified entrypoint.
- [Risk] Adding workflow linkage may complicate data relationships. → Mitigation: keep links optional and well-defined through task IDs in journal and follow-up items.
- [Risk] A single terminal UI may become too noisy for users. → Mitigation: use concise summary sections and highlight only the next actions.
