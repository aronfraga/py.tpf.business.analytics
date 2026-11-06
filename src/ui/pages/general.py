from typing import Dict, List
import plotly.graph_objects as go
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.dummy_common import SUBJECTS
from data.dummy_general import ACTIVE_INACTIVE, GENERAL_INTERPRETATION, GENERAL_KPIS, GRADE_DISTRIBUTION, PARTICIPATION_TREND
from ui.components.cards import card_row
from ui.components.charts import grouped_bar_chart, multi_line_chart, show_figure
from ui.components.texts import interpretation, section_title

def show() -> None:
    page_title: str = "General"
    st.title(page_title)
    
    for subject in SUBJECTS:
        section_title(subject)
        cards: List[Dict[str, str]] = GENERAL_KPIS[subject]
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
    
    status_figure: go.Figure = grouped_bar_chart(ACTIVE_INACTIVE, status_x, status_y, status_title, status_x_title, students_y_title)
    
    grades_x: str = "range"
    grades_y: str = "count"
    grades_title: str = "Distribución de notas"
    grades_x_title: str = "Rango de nota"
    
    grades_figure: go.Figure = grouped_bar_chart(GRADE_DISTRIBUTION, grades_x, grades_y, grades_title, grades_x_title, students_y_title)
    
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
    
    trend_figure: go.Figure = multi_line_chart(PARTICIPATION_TREND, trend_x, trend_y, trend_title, trend_x_title, trend_y_title)
    
    show_figure(trend_figure)
    interpretation(GENERAL_INTERPRETATION)

show()
