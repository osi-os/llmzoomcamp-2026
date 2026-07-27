import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import dlt

    return alt, dlt, mo


@app.cell
def _(dlt):
    dataset = dlt.dataset(destination="playground", dataset_name="agent_logs")
    return (dataset,)


@app.cell
def _(mo):
    mo.md("""
    # Agent Traces Usage Report
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Daily Activity by Project
    """)
    return


@app.cell
def _(dataset):
    df_chart1 = dataset("""
        SELECT
            date_trunc('day', timestamp) AS day,
            cwd AS project,
            count(*) AS n_events
        FROM logs
        WHERE timestamp IS NOT NULL AND cwd IS NOT NULL
        GROUP BY 1, 2
        ORDER BY 1
    """).df()
    return (df_chart1,)


@app.cell
def _(alt, df_chart1):
    _chart = alt.Chart(df_chart1).mark_line(point=True).encode(
        x="day:T",
        y="n_events:Q",
        color="project:N",
        tooltip=["day:T", "project:N", "n_events:Q"]
    ).properties(title="Daily Activity by Project")
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Most-Used Tools
    """)
    return


@app.cell
def _(dataset):
    df_chart2 = dataset("""
        SELECT
            name AS tool_name,
            count(*) AS n_calls
        FROM logs__message__content
        WHERE type = 'tool_use' AND name IS NOT NULL
        GROUP BY 1
        ORDER BY n_calls DESC
        LIMIT 15
    """).df()
    return (df_chart2,)


@app.cell
def _(alt, df_chart2):
    _chart = alt.Chart(df_chart2).mark_bar().encode(
        x=alt.X("n_calls:Q", title="Calls"),
        y=alt.Y("tool_name:N", sort="-x", title="Tool"),
        tooltip=["tool_name:N", "n_calls:Q"]
    ).properties(title="Most-Used Tools")
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Token Usage by Model
    """)
    return


@app.cell
def _(dataset):
    df_chart3 = dataset("""
        SELECT message__model AS model, 'input' AS token_type, sum(usage__input_tokens) AS tokens
        FROM logs WHERE message__model IS NOT NULL GROUP BY 1
        UNION ALL
        SELECT message__model, 'output', sum(usage__output_tokens)
        FROM logs WHERE message__model IS NOT NULL GROUP BY 1
    """).df()
    return (df_chart3,)


@app.cell
def _(alt, df_chart3):
    _chart = alt.Chart(df_chart3).mark_bar().encode(
        x=alt.X("model:N", title="Model"),
        y=alt.Y("tokens:Q", title="Tokens", stack=True),
        color="token_type:N",
        tooltip=["model:N", "token_type:N", "tokens:Q"]
    ).properties(title="Token Usage by Model")
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Activity by Project
    """)
    return


@app.cell
def _(dataset):
    df_chart4 = dataset("""
        SELECT
            cwd AS project,
            count(*) AS n_events,
            count(distinct session_id) AS n_sessions
        FROM logs
        WHERE cwd IS NOT NULL
        GROUP BY 1
        ORDER BY n_events DESC
    """).df()
    return (df_chart4,)


@app.cell
def _(alt, df_chart4):
    _chart = alt.Chart(df_chart4).mark_bar().encode(
        x=alt.X("n_events:Q", title="Events"),
        y=alt.Y("project:N", sort="-x", title="Project"),
        tooltip=["project:N", "n_events:Q", "n_sessions:Q"]
    ).properties(title="Activity by Project")
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Activity by Git Branch
    """)
    return


@app.cell
def _(dataset):
    df_chart5 = dataset("""
        SELECT
            git_branch,
            count(*) AS n_events
        FROM logs
        WHERE git_branch IS NOT NULL
        GROUP BY 1
        ORDER BY n_events DESC
    """).df()
    return (df_chart5,)


@app.cell
def _(alt, df_chart5):
    _chart = alt.Chart(df_chart5).mark_bar().encode(
        x=alt.X("n_events:Q", title="Events"),
        y=alt.Y("git_branch:N", sort="-x", title="Branch"),
        tooltip=["git_branch:N", "n_events:Q"]
    ).properties(title="Activity by Git Branch")
    _chart
    return


if __name__ == "__main__":
    app.run()
