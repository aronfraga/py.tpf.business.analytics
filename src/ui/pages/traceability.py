import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data.dummy_common import SUBJECTS
from data.dummy_traceability import ACTIVITY_HEATMAP, INTERACTIONS_BY_ACTION, TIMELINE, TRACEABILITY_INTERPRETATION
from ui.components.charts import heatmap, horizontal_bar_chart, line_chart, show_figure
from ui.components.filters import selector
from ui.components.texts import interpretation, section_title

def show() -> None:
    page_title: str = "Trazabilidad"
    st.title(page_title)
    subject_label: str = "Asignatura"
    subject_key: str = "traceability_subject"
    subject: str = selector(subject_label, SUBJECTS, subject_key)
    by_action: pd.DataFrame = INTERACTIONS_BY_ACTION[subject]
    heat: pd.DataFrame = ACTIVITY_HEATMAP[subject]
    timeline: pd.DataFrame = TIMELINE[subject]
    text: str = TRACEABILITY_INTERPRETATION[subject]
    interactions_section: str = "Interacciones"
    section_title(interactions_section)
    
    value_column: str = "count"
    category_column: str = "action"
    actions_title: str = "Interacciones por tipo de acción"
    actions_x_title: str = "Interacciones"
    actions_figure: go.Figure = horizontal_bar_chart(by_action, value_column, category_column, actions_title, actions_x_title)
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
    timeline_figure: go.Figure = line_chart(timeline, date_column, interactions_column, timeline_title, date_title, timeline_y_title) 
    show_figure(timeline_figure)
    
    interpretation(text)

show()
