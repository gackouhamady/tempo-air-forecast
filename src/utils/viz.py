import plotly.graph_objects as go


def line_chart(ts_df, y_cols, title="Time Series"):
    fig = go.Figure()
    for c in y_cols:
        fig.add_trace(go.Scatter(x=ts_df.index, y=ts_df[c], mode="lines", name=c))
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Value", height=350)
    return fig
