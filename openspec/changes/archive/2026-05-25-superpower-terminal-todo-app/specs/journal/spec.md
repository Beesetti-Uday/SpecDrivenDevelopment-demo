## ADDED Requirements

### Requirement: Record journal entries
The system SHALL allow users to create journal entries that capture reflections and progress notes within the terminal app.

#### Scenario: Add a journal entry
- **WHEN** the user writes a new journal entry with a title and content
- **THEN** the system stores the entry and makes it retrievable by date or tag

### Requirement: Link journal entries to tasks
The system SHALL allow users to associate journal entries with specific todos or recurring task contexts.

#### Scenario: Attach journal entry to a task
- **WHEN** the user links a journal entry to an existing todo item
- **THEN** the system stores the reference and makes the association visible in the task context
