## Why

The current monitoring system tracks model availability and latency, but lacks model metadata intelligence. Users need to understand what each model is best at (vendor, use cases like coding/chatting/document writing, Chinese language proficiency) without manually researching each model. Automating this via AI classification using a config-specified model improves both efficiency and user experience.

## What Changes

- **New `model_tags` table**: Stores AI-generated categorization for each model (vendor, use cases, language strengths)
- **New categorization workflow**: On each health check, if a model has no tags, invoke AI classification using the configured classifier model
- **Configurable classifier**: Add `classifier.model` to `config.yaml` to specify which model to use for classification
- **Tag display**: Frontend shows tags on model cards and supports tag-based filtering/search
- **Skip if classified**: Already-categorized models are skipped to avoid redundant AI calls
- **Tag persistence**: Tags survive across restarts and are stored in SQLite

## Capabilities

### New Capabilities
- `model-categorization`: AI-powered model tag classification stored in database
- `model-tags-api`: API endpoints to query models by tags and display tag metadata

### Modified Capabilities
- None (new capability only)

## Impact

- **Database**: New `model_tags` table in `data/monitor.db`
- **Config**: New `classifier.model` setting in `config.yaml`
- **NewAPI Adapter**: Added method to call AI classification using configured classifier model
- **Health Monitor**: Integration point to trigger categorization on uncategorized models
- **Web API**: New endpoints for tag-based model search/filter
- **Frontend**: Tag display and tag filter UI on model cards
