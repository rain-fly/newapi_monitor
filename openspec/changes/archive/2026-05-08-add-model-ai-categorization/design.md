## Context

The NewAPI Model Monitor currently tracks availability and latency for 40+ models, but provides no metadata about what each model is best at. Users viewing the dashboard must manually research each model to understand its vendor, primary use cases (coding, chat, document writing), and language capabilities.

## Goals / Non-Goals

**Goals:**
- Automatically classify models using AI when first discovered
- Extract: vendor (厂商), use cases (编程/聊天/写文档), Chinese proficiency (擅长中文)
- Persist tags in SQLite for fast lookup
- Display tags in frontend and allow filtering by tag
- Minimize AI API calls by classifying each model only once

**Non-Goals:**
- Real-time re-classification (tags are static once set)
- Complex tag hierarchies or user-defined tags
- Support for other AI classification providers (only use NewAPI itself)
- Guarantee classification accuracy (AI-generated, best-effort)

## Decisions

### 1. Classification Trigger: Lazy On-First-Seen

**Decision:** Classify a model when it first appears AND has no existing tags, not eagerly on startup.

**Why:** Avoids unnecessary AI calls during regular health checks. The agent already calls `get_available_models()` each cycle — if `model_tags` has no entry for that model, trigger classification.

**Alternative:** Batch classify all uncategorized models on startup.
- **Rejected:** High latency on first run, wasteful if many models already classified.

### 2. AI Model for Classification: Config-Specified Model

**Decision:** Use a dedicated classification model specified in `config.yaml` instead of dynamically selecting the lowest-latency model.

**Why:** Predictable behavior, easier to debug, and the operator can choose a fast/cheap model for classification. Classification is a one-shot operation per model, so runtime efficiency is less critical.

**Config:**
```yaml
classifier:
  model: "gpt-4o-mini"   # Model used for AI classification
```

**Alternative:** Lowest-latency model.
- **Rejected:** Dynamic selection adds complexity and may select a suboptimal model if latency data is stale.

### 3. Tag Storage: Separate `model_tags` Table

**Decision:** Create a dedicated `model_tags` table instead of embedding in `test_records`.

```sql
CREATE TABLE model_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT UNIQUE NOT NULL,
    vendor TEXT,
    use_cases TEXT,          -- JSON array: ["coding", "chat", "docs"]
    language_strengths TEXT, -- JSON array: ["chinese", "english"]
    raw_response TEXT,       -- Full AI response for debugging
    classified_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Why:** Separation of concerns. Tags are metadata, not test results. Enables efficient tag-based queries without joining large test tables.

### 4. Classification Prompt Strategy: Structured Output

**Decision:** Request JSON-structured response from AI with explicit fields.

**Prompt design:**
```
Classify the AI model "{model_name}" based on its name and common knowledge.
Return JSON: {"vendor": "...", "use_cases": [...], "language_strengths": [...]}
- vendor: company or project name (e.g., "OpenAI", "DeepSeek", "Google")
- use_cases: array of best-suited tasks (e.g., "coding", "chat", "docs", "reasoning")
- language_strengths: array of languages model excels at (e.g., "chinese", "english", "code")
```

**Why:** Structured JSON avoids parsing ambiguity. Explicit field names guide the AI.

### 5. API for Tags: Extend Existing Endpoints

**Decision:** Add tag data to existing `/api/models` response and new `/api/tags` endpoint.

**Why:** No new frontend endpoints needed. Existing `GET /api/models` already returns model list — add tags field. New `/api/tags` for tag cloud/filter UI.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| AI classification uses quota on fastest model | Classification is one-shot per model; tags persist indefinitely |
| Classification prompt may not work for obscure models | Include fallback: if model name unrecognizable, use "unknown" values |
| Concurrent classification requests | Use a lock/mutex — only one classification at a time during health check |
| Tags may become stale if model capabilities change | Non-goal: tags are best-effort, static once set |

## Open Questions

1. Should vendor extraction from model name use regex/heuristics (e.g., `gpt-*` → OpenAI) before calling AI?
2. Maximum number of tags per category? (e.g., max 5 use cases)
3. Should we store a "confidence" score from AI response?
