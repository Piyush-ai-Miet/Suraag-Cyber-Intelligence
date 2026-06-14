"""
modules/traffic_patterns.py — Suराग Traffic Timeline & Heatmap
Generates 24-hour bar charts and day/hour heatmaps using Plotly.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from config import COLOR_BG, COLOR_CARD, COLOR_ACCENT, COLOR_CRITICAL, COLOR_TEXT, COLOR_MUTED

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLOR_BG,
    plot_bgcolor=COLOR_CARD,
    font=dict(color=COLOR_TEXT, family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="#21262D", zerolinecolor="#21262D"),
    yaxis=dict(gridcolor="#21262D", zerolinecolor="#21262D"),
)


@st.cache_data(show_spinner=False)
def build_hourly_timeline(df: pd.DataFrame) -> go.Figure:
    """
    24-hour session bar chart.
    Bars for hours 0–4 are highlighted in red (fraud window).
    Peak hour is annotated automatically.
    """
    hourly = df.groupby("Hour_IST").size().reindex(range(24), fill_value=0).reset_index()
    hourly.columns = ["Hour", "Sessions"]

    colors = [
        COLOR_CRITICAL if h < 5 else COLOR_ACCENT
        for h in hourly["Hour"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hourly["Hour"],
        y=hourly["Sessions"],
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="<b>%{x}:00 IST</b><br>Sessions: %{y}<extra></extra>",
    ))

    # Annotate peak hour
    peak_row = hourly.loc[hourly["Sessions"].idxmax()]
    fig.add_annotation(
        x=peak_row["Hour"],
        y=peak_row["Sessions"],
        text=f"  ⬆ Peak: {int(peak_row['Sessions'])} sessions",
        showarrow=False,
        font=dict(color=COLOR_ACCENT, size=12),
        yshift=12,
        xanchor="left",
    )

    # Red shading for 0–5 AM fraud window
    fig.add_vrect(x0=-0.5, x1=4.5, fillcolor=COLOR_CRITICAL, opacity=0.08,
                  line_width=0, annotation_text="Fraud Window (12 AM–5 AM)",
                  annotation_position="top left",
                  annotation_font_color=COLOR_CRITICAL,
                  annotation_font_size=11)

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Sessions by Hour (IST)", font=dict(size=16, color=COLOR_TEXT)),
        xaxis_tickmode="linear",
        xaxis_tick0=0,
        xaxis_dtick=1,
        xaxis_title="Hour of Day (IST)",
        yaxis_title="Number of Sessions",
        showlegend=False,
    )
    return fig


@st.cache_data(show_spinner=False)
def build_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Day × Hour heatmap — rows = days of week, columns = hours.
    Uses deep navy → cyan color scale.
    """
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = (
        df.groupby(["DayOfWeek", "Hour_IST"])
        .size()
        .unstack(fill_value=0)
        .reindex(day_order, fill_value=0)
    )
    # Ensure all hours present
    for h in range(24):
        if h not in pivot.columns:
            pivot[h] = 0
    pivot = pivot[sorted(pivot.columns)]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=pivot.index.tolist(),
        colorscale=[[0, "#0D1117"], [0.5, "#1B4F72"], [1.0, COLOR_ACCENT]],
        hovertemplate="<b>%{y} at %{x}</b><br>Sessions: %{z}<extra></extra>",
        colorbar=dict(
            title="Sessions",
            tickfont=dict(color=COLOR_TEXT),
            title_font=dict(color=COLOR_TEXT),
        ),
    ))

    # Add red marker for fraud window columns (0–4)
    for h in range(5):
        fig.add_vline(x=h - 0.5, line_color=COLOR_CRITICAL, line_width=1, opacity=0.3)

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Activity Heatmap: Day × Hour", font=dict(size=16, color=COLOR_TEXT)),
        xaxis_title="Hour (IST)",
        yaxis_title="Day of Week",
    )
    return fig


@st.cache_data(show_spinner=False)
def build_subscriber_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Multi-subscriber timeline — each subscriber a different colored line.
    Used primarily on Page 2 for gang activity overlap.
    """
    colors = [COLOR_ACCENT, "#FF8C00", "#3FB950", "#FF4444", "#9B59B6", "#E74C3C"]

    fig = go.Figure()
    subscribers = df["Subscriber_ID"].unique()

    for i, sub_id in enumerate(subscribers):
        df_sub = df[df["Subscriber_ID"] == sub_id]
        name   = df_sub["Subscriber_Name"].iloc[0]
        hourly = df_sub.groupby("Hour_IST").size().reindex(range(24), fill_value=0)

        fig.add_trace(go.Scatter(
            x=list(range(24)),
            y=hourly.values,
            name=f"{name}",
            line=dict(color=colors[i % len(colors)], width=2),
            mode="lines+markers",
            marker=dict(size=5),
            hovertemplate=f"<b>{name}</b><br>Hour: %{{x}}:00<br>Sessions: %{{y}}<extra></extra>",
        ))

    # Fraud window shading
    fig.add_vrect(x0=-0.5, x1=4.5, fillcolor=COLOR_CRITICAL, opacity=0.08, line_width=0)

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Suspect Activity — 24-Hour Comparison", font=dict(size=16, color=COLOR_TEXT)),
        xaxis_tickmode="linear",
        xaxis_tick0=0,
        xaxis_dtick=2,
        xaxis_title="Hour of Day (IST)",
        yaxis_title="Sessions",
        legend=dict(bgcolor=COLOR_CARD, bordercolor=COLOR_ACCENT, borderwidth=1,
                    font=dict(color=COLOR_TEXT)),
    )
    return fig


def get_peak_hour_summary(df: pd.DataFrame) -> str:
    """Return a plain-English sentence about peak activity."""
    hourly = df.groupby("Hour_IST").size()
    peak_hour = int(hourly.idxmax())
    peak_count = int(hourly.max())
    off = peak_hour < 5

    time_label = f"{peak_hour:02d}:00 IST"
    warning = " — this is deep in the night, far outside normal working hours, which is a strong indicator of deliberate suspicious activity." if off else "."
    return (
        f"The busiest period was at **{time_label}** with **{peak_count} sessions**{warning}"
    )
