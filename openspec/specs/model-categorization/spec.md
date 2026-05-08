## ADDED Requirements

### Requirement: Model tags table exists
The system SHALL store model classification tags in a `model_tags` SQLite table with fields: `model` (TEXT, UNIQUE), `vendor` (TEXT), `use_cases` (TEXT JSON array), `language_strengths` (TEXT JSON array), `raw_response` (TEXT), `classified_at` (TEXT), `updated_at` (TEXT).

#### Scenario: Table creation on first run
- **WHEN** the application starts and `model_tags` table does not exist
- **THEN** the system SHALL create the table with all defined columns

#### Scenario: Index creation for performance
- **WHEN** the table is created
- **THEN** the system SHALL create an index on `model` column for fast lookups

### Requirement: Unclassified models trigger AI classification
During the health check cycle, if a model has no entry in `model_tags`, the system SHALL invoke AI classification using the configured classifier model from `config.yaml`.

#### Scenario: Model without tags triggers classification
- **WHEN** health check finds a model M with no entry in `model_tags`
- **THEN** the system SHALL read the classifier model name from `config.yaml` under `classifier.model`
- **AND** the system SHALL send a classification prompt to that configured model
- **AND** the system SHALL parse the JSON response and store tags in `model_tags`

#### Scenario: Model with existing tags is skipped
- **WHEN** health check finds a model M that already has an entry in `model_tags`
- **THEN** the system SHALL skip classification for that model

#### Scenario: Classification uses configured model
- **WHEN** a classification is needed
- **THEN** the system SHALL use the model specified in `config.yaml` under `classifier.model`
- **AND** if the configured model is unavailable, classification SHALL be skipped for that cycle

### Requirement: Classification prompt produces structured output
The classification prompt SHALL request JSON with `vendor`, `use_cases` (array), and `language_strengths` (array) fields.

#### Scenario: Classification prompt format
- **WHEN** the system sends a classification request
- **THEN** the prompt SHALL include the model name to classify
- **AND** the prompt SHALL request JSON with exact fields: `vendor`, `use_cases`, `language_strengths`
- **AND** the prompt SHALL indicate acceptable values for each field

#### Scenario: Fallback for unrecognizable model
- **WHEN** the AI response cannot be parsed or model is unknown
- **THEN** the system SHALL store "unknown" for vendor and empty arrays for use_cases and language_strengths
- **AND** the raw response SHALL still be stored in `raw_response` for debugging

### Requirement: Classification is idempotent
Multiple classification attempts for the same model SHALL NOT create duplicate entries. If `model` already exists in `model_tags`, the system SHALL update the existing row.

#### Scenario: Re-classification updates existing row
- **WHEN** a classification is triggered for a model that already has tags
- **THEN** the system SHALL update the existing `model_tags` row
- **AND** `updated_at` SHALL reflect the new classification time

### Requirement: Classification happens only one at a time
The system SHALL use a threading lock to ensure only one AI classification request is in flight at any time.

#### Scenario: Concurrent classification requests are blocked
- **WHEN** two health check cycles both detect the same unclassified model
- **THEN** only one SHALL perform classification
- **AND** the other SHALL wait for the lock and skip (tags now exist)
