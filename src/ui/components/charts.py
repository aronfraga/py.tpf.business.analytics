from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui.components.template import GROUP_COLORS, GROUP_ORDER, HEATMAP_SCALE, TEMPLATE, TRANSPARENT, TREND_COLOR

def apply_template(figure: go.Figure, title: str, x_title: str, y_title: str) -> go.Figure:
    figure.layout.template = TEMPLATE
    figure.update_layout(title_text=title)
    figure.update_xaxes(title_text=x_title)
    figure.update_yaxes(title_text=y_title)
    return figure

def bar_chart(table: pd.DataFrame, x_column: str, y_column: str, title: str, x_title: str, y_title: str) -> go.Figure:
    x_values: List[Any] = table[x_column].tolist()
    y_values: List[Any] = table[y_column].tolist()
    
    text_position: str = "outside"
    clip_on_axis: bool = False
    
    trace: go.Bar = go.Bar(x=x_values, y=y_values, text=y_values, textposition=text_position, cliponaxis=clip_on_axis)
    traces: List[go.Bar] = [trace]
    
    figure: go.Figure = go.Figure(data=traces)
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    
    return result

def horizontal_bar_chart(table: pd.DataFrame, value_column: str, category_column: str, title: str, x_title: str) -> go.Figure:
    values: List[Any] = table[value_column].tolist()
    categories: List[Any] = table[category_column].tolist()
    
    orientation: str = "h"
    text_position: str = "outside"
    clip_on_axis: bool = False
    
    trace: go.Bar = go.Bar(x=values, y=categories, orientation=orientation, text=values, textposition=text_position, cliponaxis=clip_on_axis)
    
    traces: List[go.Bar] = [trace]
    figure: go.Figure = go.Figure(data=traces)
    
    autorange: str = "reversed"
    label_standoff: int = 10
    
    figure.update_yaxes(autorange=autorange, ticklabelstandoff=label_standoff)
    
    y_title: str = ""
    
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    return result

def grouped_bar_chart(series: Dict[str, pd.DataFrame], x_column: str, y_column: str, title: str, x_title: str, y_title: str) -> go.Figure:
    figure: go.Figure = go.Figure()
    
    for name, table in series.items():
        x_values: List[Any] = table[x_column].tolist()
        y_values: List[Any] = table[y_column].tolist()
        trace: go.Bar = go.Bar(name=name, x=x_values, y=y_values)
        figure.add_trace(trace)
    
    bar_mode: str = "group"
    figure.update_layout(barmode=bar_mode)
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    
    return result

def histogram(table: pd.DataFrame, x_column: str, y_column: str, title: str, x_title: str, y_title: str) -> go.Figure:
    x_values: List[Any] = table[x_column].tolist()
    y_values: List[Any] = table[y_column].tolist()
    
    trace: go.Bar = go.Bar(x=x_values, y=y_values)
    traces: List[go.Bar] = [trace]
    figure: go.Figure = go.Figure(data=traces)
    bar_gap: float = 0.04
    
    figure.update_layout(bargap=bar_gap)
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    
    return result

def line_chart(table: pd.DataFrame, x_column: str, y_column: str, title: str, x_title: str, y_title: str) -> go.Figure:
    x_values: List[Any] = table[x_column].tolist()
    y_values: List[Any] = table[y_column].tolist()
    mode: str = "lines+markers"
    line: Dict[str, int] = {"width": 3}
    trace: go.Scatter = go.Scatter(x=x_values, y=y_values, mode=mode, line=line)
    traces: List[go.Scatter] = [trace]
    figure: go.Figure = go.Figure(data=traces)
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    
    return result

def multi_line_chart(series: Dict[str, pd.DataFrame], x_column: str, y_column: str, title: str, x_title: str, y_title: str) -> go.Figure:
    figure: go.Figure = go.Figure()
    mode: str = "lines+markers"
    line: Dict[str, int] = {"width": 3}
    
    for name, table in series.items():
        x_values: List[Any] = table[x_column].tolist()
        y_values: List[Any] = table[y_column].tolist()
        trace: go.Scatter = go.Scatter(name=name, x=x_values, y=y_values, mode=mode, line=line)
        figure.add_trace(trace)
    
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    return result

def donut_chart(table: pd.DataFrame, label_column: str, value_column: str, title: str) -> go.Figure:
    labels: List[Any] = table[label_column].tolist()
    values: List[Any] = table[value_column].tolist()
    hole: float = 0.55
    sort: bool = False
    trace: go.Pie = go.Pie(labels=labels, values=values, hole=hole, sort=sort)
    traces: List[go.Pie] = [trace]
    figure: go.Figure = go.Figure(data=traces)
    figure.layout.template = TEMPLATE
    figure.update_layout(title_text=title)
    
    return figure

def heatmap(table: pd.DataFrame, title: str, x_title: str, y_title: str) -> go.Figure:
    matrix: List[Any] = table.values.tolist()
    columns: List[Any] = table.columns.tolist()
    rows: List[Any] = table.index.tolist()
    
    gap: int = 3
    colorbar_title_text: str = "Total"
    colorbar_title: Dict[str, str] = {"text": colorbar_title_text}
    colorbar: Dict[str, Any] = {"thickness": 12, "title": colorbar_title}
    trace: go.Heatmap = go.Heatmap(z=matrix, x=columns, y=rows, colorscale=HEATMAP_SCALE, xgap=gap, ygap=gap, colorbar=colorbar)
    traces: List[go.Heatmap] = [trace]
    figure: go.Figure = go.Figure(data=traces)
    autorange: str = "reversed"
    figure.update_yaxes(autorange=autorange)
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    
    return result

def scatter_with_trend(points: pd.DataFrame, trend: pd.DataFrame, x_column: str, y_column: str, title: str, x_title: str, y_title: str) -> go.Figure:
    points_x: List[Any] = points[x_column].tolist()
    points_y: List[Any] = points[y_column].tolist()
    trend_x: List[Any] = trend[x_column].tolist()
    trend_y: List[Any] = trend[y_column].tolist()
    points_name: str = "Estudiantes"
    points_mode: str = "markers"
    points_marker: Dict[str, Any] = {"size": 11, "opacity": 0.85}
    points_trace: go.Scatter = go.Scatter(name=points_name, x=points_x, y=points_y, mode=points_mode, marker=points_marker)
    trend_name: str = "Tendencia"
    trend_mode: str = "lines"
    trend_line: Dict[str, Any] = {"width": 3, "dash": "dash", "color": "#E0A458"}
    trend_trace: go.Scatter = go.Scatter(name=trend_name, x=trend_x, y=trend_y, mode=trend_mode, line=trend_line)
    traces: List[go.Scatter] = [points_trace, trend_trace]
    figure: go.Figure = go.Figure(data=traces)
    
    result: go.Figure = apply_template(figure, title, x_title, y_title)
    
    return result

def scatter_by_group(points: pd.DataFrame, trend: pd.DataFrame, x_column: str, y_column: str, group_column: str, title: str, x_title: str, y_title: str) -> go.Figure:
    figure: go.Figure = go.Figure()
    points_mode: str = "markers"

    for group in GROUP_ORDER:
        is_group: pd.Series = points[group_column] == group
        group_points: pd.DataFrame = points.loc[is_group]
        group_x: List[Any] = group_points[x_column].tolist()
        group_y: List[Any] = group_points[y_column].tolist()
        group_color: str = GROUP_COLORS[group]
        group_marker: Dict[str, Any] = {"size": 11, "opacity": 0.85, "color": group_color}
        group_trace: go.Scatter = go.Scatter(name=group, x=group_x, y=group_y, mode=points_mode, marker=group_marker)
        figure.add_trace(group_trace)

    trend_x: List[Any] = trend[x_column].tolist()
    trend_y: List[Any] = trend[y_column].tolist()
    trend_name: str = "Tendencia"
    trend_mode: str = "lines"
    trend_line: Dict[str, Any] = {"width": 3, "dash": "dash", "color": TREND_COLOR}
    trend_trace: go.Scatter = go.Scatter(name=trend_name, x=trend_x, y=trend_y, mode=trend_mode, line=trend_line)
    figure.add_trace(trend_trace)

    legend_position: Dict[str, Any] = {"y": -0.32}
    bottom_margin: Dict[str, int] = {"b": 110}
    figure.update_layout(legend=legend_position, margin=bottom_margin)
    result: go.Figure = apply_template(figure, title, x_title, y_title)

    return result

def show_figure(figure: go.Figure) -> None:
    figure.update_layout(plot_bgcolor=TRANSPARENT, paper_bgcolor=TRANSPARENT)
    theme: Optional[str] = None
    display_mode_bar: bool = False
    config: Dict[str, Any] = {"displayModeBar": display_mode_bar}
    st.plotly_chart(figure, theme=theme, config=config)
