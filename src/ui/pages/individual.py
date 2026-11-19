from typing import Any, Dict, List, Optional, Tuple
from streamlit.delta_generator import DeltaGenerator
from data.real_individual import build_all
from ui.components.charts import (
    bar_chart, bar_chart_by_subject, horizontal_bar_chart, line_chart, multi_line_chart, show_figure)
from ui.components.filters import selector
from ui.components.tables import table
from ui.components.texts import section_title
from ui.components.traffic_light import traffic_light
from constants import GRADES_LABELS, SUBJECT_ALL
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ALL_GRADES_LABELS: Dict[str, str] = {"subject": "Asignatura", "instrument": "Instrumento", "grade": "Nota"}

def show_traffic_lights(lights: List[Tuple[Optional[str], str, str]]) -> None:
    columns: List[DeltaGenerator] = st.columns(len(lights))
    index: int = 0

    for subject_name, color, text in lights:
        with columns[index]:
            if subject_name is None:
                traffic_light(color, text)
            else:
                traffic_light(color, text, subject_name)
        index = index + 1

def show() -> None:
    page_title: str = "Individual"
    st.title(page_title)

    students: List[str]
    student_data: Dict[str, Dict[str, Dict[str, Any]]]
    student_subjects: Dict[str, List[str]]
    students, student_data, student_subjects = build_all()

    column_count: int = 2
    student_column: DeltaGenerator
    subject_column: DeltaGenerator
    student_column, subject_column = st.columns(column_count)
    student_label: str = "Estudiante"
    student_key: str = "individual_student"
    subject_label: str = "Asignatura"
    subject_key_prefix: str = "individual_subject_"

    with student_column:
        student: str = selector(student_label, students, student_key)
    with subject_column:
        subject_options: List[str] = [SUBJECT_ALL] + student_subjects[student]
        subject: str = selector(subject_label, subject_options, subject_key_prefix + student)

    data: Dict[str, Any] = student_data[student][subject]
    is_all: bool = subject == SUBJECT_ALL
    grades: pd.DataFrame = data["grades"]
    traceability: pd.DataFrame = data["traceability"]
    lights: List[Tuple[Optional[str], str, str]] = data["traffic_lights"]
    section_title(student)
    show_traffic_lights(lights)

    charts_section: str = "Notas y participación"
    section_title(charts_section)

    instrument_column: str = "instrument"
    grade_column: str = "grade"
    grades_title: str = "Notas por instrumento"
    instrument_title: str = "Instrumento"
    grade_title: str = "Nota"

    grades_figure: go.Figure

    if is_all:
        grades_figure = bar_chart_by_subject(
            grades, instrument_column, grade_column, "subject", grades_title, instrument_title, grade_title)
    else:
        grades_figure = bar_chart(grades, instrument_column, grade_column, grades_title, instrument_title, grade_title)

    week_column: str = "week"
    sessions_column: str = "sessions"
    participation_title: str = "Participación semanal"
    week_title: str = "Semana"
    sessions_title: str = "Sesiones"

    participation_figure: go.Figure

    if is_all:
        series: Dict[str, pd.DataFrame] = data["participation_series"]
        participation_figure = multi_line_chart(
            series, week_column, sessions_column, participation_title, week_title, sessions_title)
    else:
        participation: pd.DataFrame = data["participation"]
        participation_figure = line_chart(
            participation, week_column, sessions_column, participation_title, week_title, sessions_title)

    show_figure(grades_figure)

    if is_all:
        notes: List[str] = []
        if len(data["no_grades"]) > 0:
            notes.append("Inscripto sin notas registradas en: " + ", ".join(data["no_grades"]) + ".")
        if len(data["not_enrolled"]) > 0:
            notes.append("No inscripto en: " + ", ".join(data["not_enrolled"]) + ".")
        if len(notes) > 0:
            st.caption(" ".join(notes))

    show_figure(participation_figure)

    traceability_section: str = "Trazabilidad"
    section_title(traceability_section)

    traceability_value_column: str = "count"
    traceability_category_column: str = "action"
    traceability_title: str = "Interacciones por tipo de acción"
    traceability_x_title: str = "Interacciones"
    traceability_figure: go.Figure = horizontal_bar_chart(
        traceability, traceability_value_column, traceability_category_column, traceability_title, traceability_x_title)
    show_figure(traceability_figure)

    table_title: str = "Detalle de notas"

    if is_all:
        ordered_columns: List[str] = ["subject", "instrument", "grade"]
        table(grades[ordered_columns], table_title, ALL_GRADES_LABELS)
    else:
        table(grades, table_title, GRADES_LABELS)

show()
