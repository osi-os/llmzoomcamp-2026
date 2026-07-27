# Analysis Plan: agent_logs_pipeline

## Connection
pipeline: agent_logs_pipeline
dataset: agent_logs
destination: playground

**Special connection** (dltHub Platform Playground destination — not local duckdb):
```python
pipeline = dlt.attach("agent_traces", destination="playground", dataset_name="agent_logs")
dataset = pipeline.dataset()
```
Profiled locally against the schema-identical local DuckDB copy of `agent_logs_pipeline` (same source/transform code, same 1,000,000-row load) since the `playground` destination only resolves inside the deployed dltHub Runtime, not from a local Python process.

## Profile Summary
| table | rows | key columns | notes |
|-------|------|-------------|-------|
| logs | 1,000,000 | uuid (PK), type, session_id, timestamp, cwd, git_branch, message__role, message__model, message__stop_reason, usage__input_tokens, usage__output_tokens | type: assistant 655,982 / user 344,018. 4 models (~25% each). 5 projects (cwd), ~125k sessions. timestamp spans 2026-01-01 to 2026-03-23. git_branch: main/dev/fix/pagination/feat/standalone-in-process (4 values, ~25% each). No PII. |
| logs__message__content | 983,938 | type (text/tool_use), name (tool name), _dlt_parent_id | one row per content block; `name` populated for tool_use blocks only (8 distinct tools, ~41k calls each) |

No PII-flagged columns used in charts (cwd is a fake project path, not personal data).

## Questions
1. [x] How does activity trend day to day, and across which projects? → Chart 1
2. [x] Which tools are used most often? → Chart 2
3. [x] How much token usage (input/output) is generated, broken down by model? → Chart 3
4. [x] How is activity distributed across projects? → Chart 4
5. [x] How is activity distributed across git branches? → Chart 5

## Data Gaps
(none)

## Chart 1: Daily Activity by Project
question: How does activity trend day to day, and across which projects?
type: line
x: timestamp (daily)
y: count(*)
source: logs

```sql
SELECT
    date_trunc('day', timestamp) AS day,
    cwd AS project,
    count(*) AS n_events
FROM logs
WHERE timestamp IS NOT NULL AND cwd IS NOT NULL
GROUP BY 1, 2
ORDER BY 1
```

```altair
alt.Chart(df).mark_line(point=True).encode(
    x="day:T",
    y="n_events:Q",
    color="project:N",
    tooltip=["day:T", "project:N", "n_events:Q"]
).properties(title="Daily Activity by Project")
```

## Chart 2: Most-Used Tools
question: Which tools are used most often?
type: bar
x: count(*)
y: name (tool)
source: logs__message__content

```sql
SELECT
    name AS tool_name,
    count(*) AS n_calls
FROM logs__message__content
WHERE type = 'tool_use' AND name IS NOT NULL
GROUP BY 1
ORDER BY n_calls DESC
LIMIT 15
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("n_calls:Q", title="Calls"),
    y=alt.Y("tool_name:N", sort="-x", title="Tool"),
    tooltip=["tool_name:N", "n_calls:Q"]
).properties(title="Most-Used Tools")
```

## Chart 3: Token Usage by Model
question: How much token usage (input/output) is generated, broken down by model?
type: stacked bar
x: model
y: sum(tokens)
source: logs

```sql
SELECT message__model AS model, 'input' AS token_type, sum(usage__input_tokens) AS tokens
FROM logs WHERE message__model IS NOT NULL GROUP BY 1
UNION ALL
SELECT message__model, 'output', sum(usage__output_tokens)
FROM logs WHERE message__model IS NOT NULL GROUP BY 1
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("model:N", title="Model"),
    y=alt.Y("tokens:Q", title="Tokens", stack=True),
    color="token_type:N",
    tooltip=["model:N", "token_type:N", "tokens:Q"]
).properties(title="Token Usage by Model")
```

## Chart 4: Activity by Project
question: How is activity distributed across projects?
type: bar
x: project (cwd)
y: count(*) and distinct sessions
source: logs

```sql
SELECT
    cwd AS project,
    count(*) AS n_events,
    count(distinct session_id) AS n_sessions
FROM logs
WHERE cwd IS NOT NULL
GROUP BY 1
ORDER BY n_events DESC
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("n_events:Q", title="Events"),
    y=alt.Y("project:N", sort="-x", title="Project"),
    tooltip=["project:N", "n_events:Q", "n_sessions:Q"]
).properties(title="Activity by Project")
```

## Chart 5: Activity by Git Branch
question: How is activity distributed across git branches?
type: bar
x: git_branch
y: count(*)
source: logs

```sql
SELECT
    git_branch,
    count(*) AS n_events
FROM logs
WHERE git_branch IS NOT NULL
GROUP BY 1
ORDER BY n_events DESC
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("n_events:Q", title="Events"),
    y=alt.Y("git_branch:N", sort="-x", title="Branch"),
    tooltip=["git_branch:N", "n_events:Q"]
).properties(title="Activity by Git Branch")
```
