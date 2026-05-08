## 1. Database Changes

- [x] 1.1 Add `model_tags` table creation in `monitor/database.py`
- [x] 1.2 Add `get_model_tags(model)` method to Database class
- [x] 1.3 Add `upsert_model_tags(model, vendor, use_cases, language_strengths, raw_response)` method
- [x] 1.4 Add `get_uncategorized_models()` method to find models without tags
- [x] 1.5 Add `get_all_tags()` method for tag cloud endpoint

## 2. Config Changes

- [x] 2.1 Add `classifier` section to `config.yaml` with `model` field
- [x] 2.2 Update `config.yaml.example` with classifier configuration
- [x] 2.3 Add `classifier` property to `Config` class in `monitor/config.py`

## 3. Adapter Changes

- [x] 3.1 Add `classify_model(model_name, classifier_model)` method in `monitor/adapter.py`
- [x] 3.2 Implement structured prompt for AI classification
- [x] 3.3 Implement JSON response parsing with fallback for errors

## 4. Agent Changes

- [x] 4.1 Add threading lock for classification mutex in `monitor/agent.py`
- [x] 4.2 Integrate classification trigger after health check in `run_test()`
- [x] 4.3 Skip models that already have tags in `model_tags` table

## 5. API Changes

- [x] 5.1 Add `tags` field to `GET /api/models` response
- [x] 5.2 Add `vendor`, `use_case`, `lang` query parameter filters to `GET /api/models`
- [x] 5.3 Add `GET /api/tags` endpoint for tag cloud
- [x] 5.4 Add `tags` field to `GET /api/status` response

## 6. Frontend Changes

- [x] 6.1 Display tags on model cards in the dashboard
- [x] 6.2 Add tag filter UI (by vendor, use case, language)
- [x] 6.3 Style tags with badges or chips
