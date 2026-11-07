import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.dummy_common import SUBJECTS
from data.dummy_performance import COURSE_STATUS, GRADE_HISTOGRAM, INSTRUMENT_COMPARISON, PERFORMANCE_INTERPRETATION
from ui.components.charts import bar_chart, donut_chart, histogram, show_figure
from ui.components.filters import selector
from ui.components.texts import interpretation, section_title

def show() -> None:
    page_title: str = "Rendimiento Académico"
    st.title(page_title)
    
    subject_label: str = "Asignatura"
    subject_key: str = "performance_subject"
    subject: str = selector(subject_label, SUBJECTS, subject_key)
    instruments: pd.DataFrame = INSTRUMENT_COMPARISON[subject]
    grades: pd.DataFrame = GRADE_HISTOGRAM[subject]
    status: pd.DataFrame = COURSE_STATUS[subject]
    text: str = PERFORMANCE_INTERPRETATION[subject]
    instruments_section: str = "Instrumentos de evaluación"
    section_title(instruments_section)
    
    instrument_column: str = "instrument"
    average_column: str = "average"
    instruments_title: str = "Promedio por instrumento"
    instruments_x_title: str = "Instrumento"
    instruments_y_title: str = "Nota promedio"
    instruments_figure: go.Figure = bar_chart(instruments, instrument_column, average_column, instruments_title, instruments_x_title, instruments_y_title)
    show_figure(instruments_figure)
    
    grades_section: str = "Notas y condición"
    section_title(grades_section)
    
    column_count: int = 2
    histogram_column: DeltaGenerator
    status_column: DeltaGenerator
    histogram_column, status_column = st.columns(column_count)
    range_column: str = "range"
    count_column: str = "count"
    histogram_title: str = "Histograma de notas"
    histogram_x_title: str = "Rango de nota"
    histogram_y_title: str = "Estudiantes"
    histogram_figure: go.Figure = histogram(grades, range_column, count_column, histogram_title, histogram_x_title, histogram_y_title)
    status_label_column: str = "status"
    status_title: str = "Libre / Regular / Promociona"
    status_figure: go.Figure = donut_chart(status, status_label_column, count_column, status_title)
    
    with histogram_column:
        show_figure(histogram_figure)
    with status_column:
        show_figure(status_figure)
    interpretation(text)

show()
