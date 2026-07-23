# Analysis Plan: claude_logs_pipeline

## Connection
pipeline: claude_logs_pipeline
dataset: claude_logs
destination: duckdb

## Profile Summary
| table | rows | key columns | notes |
|-------|------|-------------|-------|
| logs | 681 | type, session_id, timestamp, cwd, message__role, message__model, message__usage__* tokens, tool_use_result__success | very wide (~150 cols) & sparse — shape varies a lot by `type`; `tool_use_result__success` is single-valued (all True, n=4) and not chart-worthy |
| logs__message__content | 493 | type (text/tool_use/tool_result/thinking), name (tool name), _dlt_root_id | one row per content block within a message; `name` populated only for tool_use blocks |

No PII-flagged columns used in charts (cwd is a local file path, not personal data beyond username already visible to the user).

## Questions
1. [x] How does my Claude Code activity trend day to day, and across which projects? → Chart 1
2. [x] Which tools do I use most often? → Chart 2
3. [x] How much token usage (input/output/cache) am I generating, broken down by model? → Chart 3
4. [x] How is my activity distributed across projects? → Chart 4
5. [x] What's the breakdown of log record types (assistant/user/system/etc.)? → Chart 5

## Data Gaps
(none)

## Chart 1: Daily Activity by Project
question: How does my Claude Code activity trend day to day, and across which projects?
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
).properties(title="Daily Claude Code Activity by Project")
```

## Chart 2: Most-Used Tools
question: Which tools do I use most often?
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
question: How much token usage (input/output/cache) am I generating, broken down by model?
type: stacked bar
x: model
y: sum(tokens)
source: logs

```sql
SELECT message__model AS model, 'input' AS token_type, sum(message__usage__input_tokens) AS tokens
FROM logs WHERE message__model IS NOT NULL GROUP BY 1
UNION ALL
SELECT message__model, 'output', sum(message__usage__output_tokens)
FROM logs WHERE message__model IS NOT NULL GROUP BY 1
UNION ALL
SELECT message__model, 'cache_read', sum(message__usage__cache_read_input_tokens)
FROM logs WHERE message__model IS NOT NULL GROUP BY 1
UNION ALL
SELECT message__model, 'cache_creation', sum(message__usage__cache_creation_input_tokens)
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
question: How is my activity distributed across projects?
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

## Chart 5: Log Record Type Breakdown
question: What's the breakdown of log record types (assistant/user/system/etc.)?
type: bar
x: type
y: count(*)
source: logs

```sql
SELECT
    type,
    count(*) AS n
FROM logs
GROUP BY 1
ORDER BY n DESC
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X("n:Q", title="Count"),
    y=alt.Y("type:N", sort="-x", title="Record Type"),
    tooltip=["type:N", "n:Q"]
).properties(title="Log Record Type Breakdown")
```
