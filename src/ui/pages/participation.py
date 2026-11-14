from typing import List
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.real_common import DATE_RANGES, SUBJECTS
from data.real_participation import get_accesses, get_activity, get_student_options
from ui.components.charts import bar_chart, line_chart, show_figure
from ui.components.filters import selector
from ui.components.texts import section_title

def show() -> None:
    page_title: str = "Participación"

    st.title(page_title)
    filter_count: int = 3
    column_count: int = 2
    subject_column: DeltaGenerator
    range_column: DeltaGenerator
    student_column: DeltaGenerator
    subject_column, range_column, student_column = st.columns(filter_count)
    subject_label: str = "Asignatura"
    subject_key: str = "participation_subject"
    range_label: str = "Rango de fechas"
    range_key: str = "participation_range"
    student_label: str = "Estudiante"
    student_key_prefix: str = "participation_student_"

    with subject_column:
        subject: str = selector(subject_label, SUBJECTS, subject_key)
    with range_column:
        date_range: str = selector(range_label, DATE_RANGES, range_key)
    with student_column:
        student_options: List[str] = get_student_options(subject)
        student_key: str = student_key_prefix + subject
        student: str = selector(student_label, student_options, student_key)

    activity: pd.DataFrame = get_activity(subject, date_range, student)
    accesses: pd.DataFrame = get_accesses(subject, date_range, student)

    section: str = "Actividad y accesos"
    section_title(section)

    date_column: str = "date"
    activity_column: str = "activities"
    activity_title: str = "Actividad por fecha"
    date_title: str = "Fecha"
    activity_y_title: str = "Actividades"
    activity_figure: go.Figure = bar_chart(activity, date_column, activity_column, activity_title, date_title, activity_y_title)
    accesses_column: str = "accesses"
    accesses_title: str = "Evolución de accesos"
    accesses_y_title: str = "Accesos"
    accesses_figure: go.Figure = line_chart(accesses, date_column, accesses_column, accesses_title, date_title, accesses_y_title)
    activity_chart_column: DeltaGenerator
    accesses_chart_column: DeltaGenerator
    activity_chart_column, accesses_chart_column = st.columns(column_count)

    with activity_chart_column:
        show_figure(activity_figure)
    with accesses_chart_column:
        show_figure(accesses_figure)

show()
