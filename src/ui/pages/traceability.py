from typing import Dict
from data.real_traceability import build_all
from ui.components.charts import heatmap, horizontal_bar_chart, line_chart, show_figure
from ui.components.filters import selector
from ui.components.texts import section_title
from constants import SUBJECT_OPTIONS
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def show() -> None:
    page_title: str = "Trazabilidad"
    st.title(page_title)
    tables: Dict[str, Dict[str, pd.DataFrame]] = build_all()
    subject_label: str = "Asignatura"
    subject_key: str = "traceability_subject"
    subject: str = selector(subject_label, SUBJECT_OPTIONS, subject_key)
    by_action: pd.DataFrame = tables["by_action"][subject]
    heat: pd.DataFrame = tables["heatmap"][subject]
    timeline: pd.DataFrame = tables["timeline"][subject]
    interactions_section: str = "Interacciones"
    section_title(interactions_section)
    
    value_column: str = "count"
    category_column: str = "action"
    actions_title: str = "Interacciones por tipo de acción"
    actions_x_title: str = "Interacciones"
    actions_figure: go.Figure = horizontal_bar_chart(
        by_action, value_column, category_column, actions_title, actions_x_title)
    show_figure(actions_figure)
    
    weekly_section: str = "Patrón semanal"
    section_title(weekly_section)
    
    heat_title: str = "Mapa de calor: día × hora"
    heat_x_title: str = "Franja horaria"
    heat_y_title: str = "Día de la semana"
    heat_figure: go.Figure = heatmap(heat, heat_title, heat_x_title, heat_y_title)
    show_figure(heat_figure)
    
    timeline_section: str = "Línea temporal"  
    section_title(timeline_section)
    
    date_column: str = "date"
    interactions_column: str = "interactions"
    timeline_title: str = "Interacciones en el tiempo"
    date_title: str = "Fecha"
    timeline_y_title: str = "Interacciones"
    timeline_figure: go.Figure = line_chart(
        timeline, date_column, interactions_column, timeline_title, date_title, timeline_y_title) 
    show_figure(timeline_figure)

show()
