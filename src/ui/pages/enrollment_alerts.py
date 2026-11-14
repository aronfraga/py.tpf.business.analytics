from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.real_common import SUBJECTS
from data.real_enrollment import ALERTS, ALERTS_LABELS, ENROLLED_NO_PARTICIPATION, ENROLLED_NO_PARTICIPATION_LABELS, ENROLLED_VS_ACTIVE, ENROLLMENT_INTERPRETATION, ENROLLMENT_KPIS, NOT_ENROLLED_ACTIVE, NOT_ENROLLED_ACTIVE_LABELS
from ui.components.cards import card_row
from ui.components.charts import bar_chart, show_figure
from ui.components.filters import selector
from ui.components.tables import table
from ui.components.texts import interpretation, section_title

def show() -> None:
    page_title: str = "Matrícula y Alertas"
    st.title(page_title)
    
    subject_label: str = "Asignatura"
    subject_key: str = "enrollment_subject"
    subject: str = selector(subject_label, SUBJECTS, subject_key)
    cards: List[Dict[str, str]] = ENROLLMENT_KPIS[subject]
    enrolled_active: pd.DataFrame = ENROLLED_VS_ACTIVE[subject]
    not_enrolled: pd.DataFrame = NOT_ENROLLED_ACTIVE[subject]
    no_participation: pd.DataFrame = ENROLLED_NO_PARTICIPATION[subject]
    alerts: pd.DataFrame = ALERTS[subject]
    text: str = ENROLLMENT_INTERPRETATION[subject]
    card_row(cards)
    
    enrolled_section: str = "Matriculados vs. activos"
    section_title(enrolled_section)
    
    status_column: str = "status"
    count_column: str = "count"
    chart_title: str = "Matriculados vs. activos"
    x_title: str = "Estado"
    y_title: str = "Estudiantes"
    figure: go.Figure = bar_chart(enrolled_active, status_column, count_column, chart_title, x_title, y_title)
    show_figure(figure)
    
    detail_section: str = "Detalle"
    section_title(detail_section)
    
    column_count: int = 2
    not_enrolled_column: DeltaGenerator
    no_participation_column: DeltaGenerator
    not_enrolled_column, no_participation_column = st.columns(column_count)
    not_enrolled_title: str = "No inscriptos activos"
    no_participation_title: str = "Inscriptos sin participación"
    
    with not_enrolled_column:
        table(not_enrolled, not_enrolled_title, NOT_ENROLLED_ACTIVE_LABELS)
    with no_participation_column:
        table(no_participation, no_participation_title, ENROLLED_NO_PARTICIPATION_LABELS)
    
    alerts_section: str = "Alertas"
    section_title(alerts_section)
    
    alerts_title: str = "Alertas de la asignatura"
    table(alerts, alerts_title, ALERTS_LABELS)
    interpretation(text)

show()
