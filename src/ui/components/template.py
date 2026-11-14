from typing import Any, Dict, List

import plotly.graph_objects as go

PALETTE: List[str] = ["#1F5C6B", "#E0A458", "#8A9BA8", "#4C9AA8", "#B5523B", "#6B8F71"]

GROUP_ORDER: List[str] = ["Promociona", "Regular", "Libre", "No se presentó"]

GROUP_COLORS: Dict[str, str] = {"Promociona": "#6B8F71", "Regular": "#E0A458", "Libre": "#B5523B", "No se presentó": "#8A9BA8"}

TREND_COLOR: str = "#1E2A32"

HEATMAP_SCALE: List[Any] = [[0.0, "#EAF3F5"], [0.5, "#6FAAB6"], [1.0, "#143F4A"]]

TRANSPARENT: str = "rgba(0,0,0,0)"

FONT_FAMILY: str = "Inter, Segoe UI, Helvetica Neue, Arial, sans-serif"

FONT: Dict[str, Any] = {"family": FONT_FAMILY, "size": 13, "color": "#4A5A64"}

MARGIN: Dict[str, int] = {"l": 24, "r": 24, "t": 56, "b": 56}

TITLE_FONT: Dict[str, Any] = {"size": 16, "color": "#1E2A32"}

TITLE: Dict[str, Any] = {"font": TITLE_FONT, "x": 0.01, "xanchor": "left"}

X_AXIS: Dict[str, Any] = {"gridcolor": "#EDF1F3", "linecolor": "#C9D3D8", "zeroline": False, "automargin": True}

Y_AXIS: Dict[str, Any] = {"gridcolor": "#EDF1F3", "linecolor": "#C9D3D8", "zeroline": False, "automargin": True}

LEGEND: Dict[str, Any] = {"orientation": "h", "yanchor": "top", "y": -0.18, "xanchor": "left", "x": 0}

HOVER_FONT: Dict[str, Any] = {"family": FONT_FAMILY, "size": 12}

HOVER_LABEL: Dict[str, Any] = {"font": HOVER_FONT}

BAR_GAP: float = 0.25

LAYOUT: go.Layout = go.Layout(colorway=PALETTE, font=FONT, paper_bgcolor=TRANSPARENT, plot_bgcolor=TRANSPARENT, margin=MARGIN, title=TITLE, xaxis=X_AXIS, yaxis=Y_AXIS, legend=LEGEND, hoverlabel=HOVER_LABEL, bargap=BAR_GAP)

TEMPLATE: go.layout.Template = go.layout.Template(layout=LAYOUT)
