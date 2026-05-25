## Why

Users need a powerful terminal-native productivity workspace that combines task management, recurring planning, and journaling in one place. This change solves the gap between simple task lists and a more introspective command-line productivity flow, making planning and follow-up easier for people who live in the terminal.

## What Changes

- Introduce a terminal app for managing todo items with recurring schedules (daily, weekly, monthly, etc.).
- Add journaling support so users can capture reflections and track progress over time.
- Support task follow-up and context-aware reminders within the same terminal workflow.

## Capabilities

### New Capabilities
- `terminal-todo`: Terminal-based task management with todo creation, editing, and completion tracking.
- `recurring-tasks`: Recurring schedule support for todos, including daily, weekly, monthly, and custom repeat patterns.
- `journal`: Journal entries and reflective notes tied to the users workflow and progress.
- `task-follow-up`: Task follow-up tools for reminders, status updates, and next-step planning.

### Modified Capabilities
- None: This change adds new capabilities without altering existing spec-level requirements.

## Impact

- Adds a new terminal application and CLI user experience.
- Introduces new data models for recurring tasks, journals, and follow-up metadata.
- May interact with existing storage or config systems if the workspace already supports terminal app state.
