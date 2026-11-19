from typing import Dict, List
from streamlit.delta_generator import DeltaGenerator
from data.services.real_general import active_inactive_for_days, build_all, general_cards_for_days
from ui.components.cards import card_row
from ui.components.charts import grouped_bar_chart, multi_line_chart, show_figure
from ui.components.texts import section_title
from constants import DEFAULT_INACTIVITY_DAYS, SUBJECTS
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def show() -> None:
    page_title: str = "General"
    st.title(page_title)

    tables: Dict[str, Dict[str, object]] = build_all()
    grade_distribution: Dict[str, pd.DataFrame] = tables["distribution"]
    participation_trend: Dict[str, pd.DataFrame] = tables["trend"]

    days_key: str = "inactivity_days"
    slider_label: str = "Días sin actividad para considerar inactivo a un alumno"
    min_days: int = 1
    max_days: int = 90
    days: int = st.slider(
        slider_label, min_value=min_days, max_value=max_days, value=DEFAULT_INACTIVITY_DAYS, key=days_key)

    for subject in SUBJECTS:
        section_title(subject)
        cards: List[Dict[str, str]] = general_cards_for_days(subject, days)
        card_row(cards)

    students_section: str = "Estudiantes y notas"
    section_title(students_section)

    column_count: int = 2
    status_column: DeltaGenerator
    grades_column: DeltaGenerator
    status_column, grades_column = st.columns(column_count)
    status_x: str = "status"
    status_y: str = "count"
    status_title: str = "Activos vs. inactivos"
    status_x_title: str = "Estado"
    students_y_title: str = "Estudiantes"
    
    active_inactive: Dict[str, pd.DataFrame] = {}
    for subject in SUBJECTS:
        active_inactive[subject] = active_inactive_for_days(subject, days)

    status_figure: go.Figure = grouped_bar_chart(
        active_inactive,status_x, status_y, status_title, status_x_title, students_y_title)
    
    grades_x: str = "range"
    grades_y: str = "count"
    grades_title: str = "Distribución de notas"
    grades_x_title: str = "Rango de nota"
    
    grades_figure: go.Figure = grouped_bar_chart(
        grade_distribution, grades_x, grades_y, grades_title, grades_x_title, students_y_title)
    
    with status_column:
        show_figure(status_figure)
    with grades_column:
        show_figure(grades_figure)
    
    participation_section: str = "Participación"
    section_title(participation_section)
    
    trend_x: str = "week"
    trend_y: str = "sessions"
    trend_title: str = "Tendencia de participación"
    trend_x_title: str = "Semana"
    trend_y_title: str = "Sesiones promedio"
    
    trend_figure: go.Figure = multi_line_chart(
        participation_trend, trend_x, trend_y, trend_title, trend_x_title, trend_y_title)
    
    show_figure(trend_figure)

show()
