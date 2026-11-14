from typing import Any, Dict
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.real_individual import GRADES_LABELS, STUDENT_DATA, STUDENTS
from ui.components.charts import bar_chart, line_chart, show_figure
from ui.components.filters import selector
from ui.components.tables import table
from ui.components.texts import section_title
from ui.components.traffic_light import traffic_light

def show() -> None:
    page_title: str = "Individual"
    st.title(page_title)
    
    student_label: str = "Estudiante"
    student_key: str = "individual_student"
    student: str = selector(student_label, STUDENTS, student_key)
    data: Dict[str, Any] = STUDENT_DATA[student]
    grades: pd.DataFrame = data["grades"]
    participation: pd.DataFrame = data["participation"]
    color: str = data["traffic_light"]
    light_text: str = data["traffic_light_text"]
    section_title(student)
    traffic_light(color, light_text)
    
    charts_section: str = "Notas y participación"
    section_title(charts_section)
    
    column_count: int = 2
    grades_column: DeltaGenerator
    participation_column: DeltaGenerator
    grades_column, participation_column = st.columns(column_count)
    
    instrument_column: str = "instrument"
    grade_column: str = "grade"
    grades_title: str = "Notas por instrumento"
    instrument_title: str = "Instrumento"
    grade_title: str = "Nota"
    
    grades_figure: go.Figure = bar_chart(grades, instrument_column, grade_column, grades_title, instrument_title, grade_title)
    
    week_column: str = "week"
    sessions_column: str = "sessions"
    participation_title: str = "Participación semanal"
    week_title: str = "Semana"
    sessions_title: str = "Sesiones"
    
    participation_figure: go.Figure = line_chart(participation, week_column, sessions_column, participation_title, week_title, sessions_title)
    
    with grades_column:
        show_figure(grades_figure)
    with participation_column:
        show_figure(participation_figure)
    
    table_title: str = "Detalle de notas"
    table(grades, table_title, GRADES_LABELS)

show()
