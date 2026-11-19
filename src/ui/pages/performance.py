from typing import Dict
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.real_performance import build_all
from ui.components.charts import bar_chart, bar_chart_by_subject, donut_chart, histogram, show_figure
from ui.components.filters import selector
from ui.components.template import GROUP_COLORS
from ui.components.texts import section_title
from constants import (
    SUBJECT_ALL,
    SUBJECT_OPTIONS,
)

def show() -> None:
    page_title: str = "Rendimiento Académico"
    st.title(page_title)

    tables: Dict[str, Dict[str, pd.DataFrame]] = build_all()

    subject_label: str = "Asignatura"
    subject_key: str = "performance_subject"
    subject: str = selector(subject_label, SUBJECT_OPTIONS, subject_key)
    instruments: pd.DataFrame = tables["instruments"][subject]
    grades: pd.DataFrame = tables["histogram"][subject]
    status: pd.DataFrame = tables["status"][subject]
    instruments_section: str = "Instrumentos de evaluación"
    section_title(instruments_section)
    
    instrument_column: str = "instrument"
    average_column: str = "average"
    instruments_title: str = "Promedio por instrumento"
    instruments_x_title: str = "Instrumento"
    instruments_y_title: str = "Nota promedio"
    instruments_figure: go.Figure

    if subject == SUBJECT_ALL:
        instruments_figure = bar_chart_by_subject(instruments, instrument_column, average_column, "subject", instruments_title, instruments_x_title, instruments_y_title)
    else:
        instruments_figure = bar_chart(instruments, instrument_column, average_column, instruments_title, instruments_x_title, instruments_y_title)

    show_figure(instruments_figure)
    
    grades_section: str = "Notas y condición"
    section_title(grades_section)
    
    column_count: int = 2
    histogram_column: DeltaGenerator
    status_column: DeltaGenerator
    histogram_column, status_column = st.columns(column_count)
    range_column: str = "range"
    count_column: str = "count"
    histogram_title: str = "Histograma de notas promedio"
    histogram_x_title: str = "Rango de nota"
    histogram_y_title: str = "Estudiantes"
    histogram_figure: go.Figure = histogram(grades, range_column, count_column, histogram_title, histogram_x_title, histogram_y_title)
    status_label_column: str = "status"
    status_title: str = "Libre / Regular / Promociona / No se presentó"
    status_colors: Dict[str, str] = {"Promociona": GROUP_COLORS["Promociona"], "Regular": GROUP_COLORS["Regular"], "Libre": GROUP_COLORS["Libre"], "No se presentó": GROUP_COLORS["No se presentó"]}
    status_figure: go.Figure = donut_chart(status, status_label_column, count_column, status_title, status_colors, "Total")
    
    with histogram_column:
        show_figure(histogram_figure)
    with status_column:
        show_figure(status_figure)

show()
