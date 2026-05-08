## ADDED Requirements

### Requirement: Tags included in model list API
The `GET /api/models` endpoint SHALL include a `tags` field for each model, containing the model's vendor, use_cases, and language_strengths.

#### Scenario: API response includes tags for classified models
- **WHEN** client calls `GET /api/models`
- **THEN** each model in the response SHALL include a `tags` object with `vendor`, `use_cases`, and `language_strengths`
- **AND** if model is unclassified, `tags` SHALL be `null`

#### Scenario: Tags field structure
- **WHEN** model has classification
- **THEN** `tags.vendor` SHALL be a string
- **AND** `tags.use_cases` SHALL be an array of strings
- **AND** `tags.language_strengths` SHALL be an array of strings

### Requirement: Tag-based model search
The system SHALL support filtering models by tag via query parameter on `GET /api/models`.

#### Scenario: Filter by vendor
- **WHEN** client calls `GET /api/models?vendor=OpenAI`
- **THEN** the response SHALL only include models where `tags.vendor` equals "OpenAI"

#### Scenario: Filter by use case
- **WHEN** client calls `GET /api/models?use_case=coding`
- **THEN** the response SHALL only include models where `tags.use_cases` contains "coding"

#### Scenario: Filter by language
- **WHEN** client calls `GET /api/models?lang=chinese`
- **THEN** the response SHALL only include models where `tags.language_strengths` contains "chinese"

#### Scenario: Combine multiple filters
- **WHEN** client calls `GET /api/models?vendor=DeepSeek&use_case=coding`
- **THEN** the response SHALL only include models matching BOTH criteria

### Requirement: Tag cloud endpoint
The `GET /api/tags` endpoint SHALL return all unique tags across all classified models.

#### Scenario: Tag cloud returns all unique values
- **WHEN** client calls `GET /api/tags`
- **THEN** the response SHALL include `vendors` (array of unique vendor strings)
- **AND** the response SHALL include `use_cases` (array of unique use case strings)
- **AND** the response SHALL include `language_strengths` (array of unique language strings)

#### Scenario: Tag cloud with counts
- **WHEN** client calls `GET /api/tags`
- **THEN** each tag value SHALL include a `count` indicating how many models have that tag

### Requirement: Status API includes tags
The `GET /api/status` endpoint SHALL include a `tags` field for each model.

#### Scenario: Status response matches models endpoint
- **WHEN** client calls `GET /api/status`
- **THEN** each model in the response SHALL include `tags` with the same structure as `GET /api/models`
