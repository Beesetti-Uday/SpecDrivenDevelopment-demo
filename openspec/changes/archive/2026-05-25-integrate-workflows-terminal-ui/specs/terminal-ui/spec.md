## ADDED Requirements

### Requirement: Unified terminal navigation
The system SHALL provide a unified terminal interface for navigating todos, recurring schedules, journal entries, and follow-up actions from a single command entrypoint.

#### Scenario: Open unified terminal UI
- **WHEN** the user runs the terminal UI command
- **THEN** the system displays the current work state, including todos, recurring items, recent journals, and pending follow-ups

### Requirement: Consistent command behavior
The system SHALL use consistent commands and flags across task, journal, and follow-up workflows in the unified terminal UI.

#### Scenario: Run a workflow command from the UI
- **WHEN** the user issues a command from the terminal UI for a task, journal, or follow-up action
- **THEN** the system executes the command and returns to the unified interface or displays the result clearly
