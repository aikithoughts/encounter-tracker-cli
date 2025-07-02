# Requirements Document

## Introduction

The D&D Encounter Tracker is a command-line application designed to help Dungeon Masters manage combat encounters during tabletop D&D sessions. The tool will track combatants, their initiative order, hit points, and combat notes, with the ability to save and load encounters for session continuity. The application is designed with future web application migration in mind.

## Requirements

### Requirement 1

**User Story:** As a Dungeon Master, I want to add combatants to an encounter, so that I can track all participants in combat.

#### Acceptance Criteria

1. WHEN I start a new encounter THEN the system SHALL allow me to add combatants with name, hit points, and initiative
2. WHEN I add a combatant THEN the system SHALL accept player characters, monsters, and NPCs as valid combatant types
3. WHEN I input combatant data THEN the system SHALL validate that required fields (name, hit points, initiative) are provided
4. WHEN I add multiple combatants THEN the system SHALL store all combatants in the current encounter

### Requirement 2

**User Story:** As a Dungeon Master, I want to view and manage initiative order, so that I can run combat in the correct sequence.

#### Acceptance Criteria

1. WHEN I view the encounter THEN the system SHALL display combatants sorted by initiative in descending order
2. WHEN two combatants have the same initiative THEN the system SHALL allow me to manually adjust their initiative values
3. WHEN I modify a combatant's initiative THEN the system SHALL automatically re-sort the initiative order
4. WHEN I view the initiative order THEN the system SHALL clearly indicate whose turn it is
5. WHEN I request to sort combatants THEN the system SHALL provide initiative order sorting (highest to lowest)
6. WHEN I sort by initiative THEN the system SHALL maintain all combatant data while reordering the display

### Requirement 3

**User Story:** As a Dungeon Master, I want to track and modify hit points, so that I can manage combat damage and healing.

#### Acceptance Criteria

1. WHEN I update hit points THEN the system SHALL accept absolute values (e.g., "15")
2. WHEN I update hit points THEN the system SHALL accept relative additions (e.g., "+5")
3. WHEN I update hit points THEN the system SHALL accept relative subtractions (e.g., "-8")
4. WHEN hit points are modified THEN the system SHALL prevent hit points from going below 0
5. WHEN I view combatants THEN the system SHALL display current hit points alongside maximum hit points

### Requirement 4

**User Story:** As a Dungeon Master, I want to add and manage notes for combatants, so that I can track status effects, spells, and tactical information.

#### Acceptance Criteria

1. WHEN I add a note to a combatant THEN the system SHALL store the note with that specific combatant
2. WHEN I view a combatant THEN the system SHALL display all associated notes
3. WHEN I add a note THEN the system SHALL allow free-form text input
4. WHEN I manage notes THEN the system SHALL allow me to edit or remove existing notes
5. WHEN I view the encounter THEN the system SHALL clearly indicate which combatants have notes

### Requirement 5

**User Story:** As a Dungeon Master, I want to save encounters to files, so that I can preserve combat state between sessions.

#### Acceptance Criteria

1. WHEN I save an encounter THEN the system SHALL write all combatant data to a file
2. WHEN I save an encounter THEN the system SHALL preserve names, hit points, initiative, and notes
3. WHEN I save an encounter THEN the system SHALL allow me to specify the filename
4. WHEN I save an encounter THEN the system SHALL use a format that supports future web application migration

### Requirement 6

**User Story:** As a Dungeon Master, I want to load encounters from files, so that I can resume previous combat sessions.

#### Acceptance Criteria

1. WHEN I load an encounter THEN the system SHALL read combatant data from the specified file
2. WHEN I load an encounter THEN the system SHALL restore all combatant names, hit points, initiative, and notes
3. WHEN I load an encounter THEN the system SHALL display the initiative order correctly
4. IF a file is corrupted or invalid THEN the system SHALL display an error message and not crash

### Requirement 7

**User Story:** As a Dungeon Master, I want an intuitive command-line interface, so that I can efficiently manage encounters during live gameplay.

#### Acceptance Criteria

1. WHEN I use the application THEN the system SHALL provide clear menu options and commands
2. WHEN I enter invalid input THEN the system SHALL display helpful error messages
3. WHEN I use commands THEN the system SHALL provide confirmation of successful actions
4. WHEN I need help THEN the system SHALL provide command documentation and examples
5. WHEN I exit the application THEN the system SHALL prompt to save unsaved changes

### Requirement 8

**User Story:** As a developer planning future migration, I want the application architecture to support web deployment, so that the core logic can be reused.

#### Acceptance Criteria

1. WHEN the application is designed THEN the system SHALL separate business logic from CLI interface
2. WHEN the application handles data THEN the system SHALL use structured data formats (JSON)
3. WHEN the application is structured THEN the system SHALL use modular components that can be adapted for web interfaces
4. WHEN the application manages state THEN the system SHALL use patterns compatible with web application frameworks