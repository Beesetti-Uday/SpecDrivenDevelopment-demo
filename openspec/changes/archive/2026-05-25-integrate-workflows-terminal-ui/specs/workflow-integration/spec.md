## ADDED Requirements

### Requirement: Link related workflow items
The system SHALL link related todos, recurring schedules, journal entries, and follow-up actions so users can trace the context across workflows.

#### Scenario: View linked workflow items
- **WHEN** the user views a task in the unified terminal UI
- **THEN** the system shows linked journal entries and follow-up actions associated with that task

### Requirement: Maintain workflow state across screens
The system SHALL preserve workflow context when moving between task lists, journal entries, and follow-up history within the terminal UI.

#### Scenario: Navigate between workflows
- **WHEN** the user navigates from a task to its journal or follow-up history
- **THEN** the system retains the task context and highlights related entries in the subsequent view
