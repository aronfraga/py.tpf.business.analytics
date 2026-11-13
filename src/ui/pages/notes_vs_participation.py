from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.real_common import SUBJECTS
from data.real_correlation import CORRELATION, CORRELATION_INTERPRETATION, SCATTER, TREND_LINE
from ui.components.cards import kpi_card
from ui.components.charts import scatter_with_trend, show_figure
from ui.components.filters import selector
from ui.components.texts import interpretation, section_title

def show() -> None:
    page_title: str = "Notas vs Participación"
    st.title(page_title)
    
    subject_label: str = "Asignatura"
    subject_key: str = "correlation_subject"
    subject: str = selector(subject_label, SUBJECTS, subject_key)
    points: pd.DataFrame = SCATTER[subject]
    trend: pd.DataFrame = TREND_LINE[subject]
    card: Dict[str, str] = CORRELATION[subject]
    text: str = CORRELATION_INTERPRETATION[subject]
    section: str = "Relación entre sesiones y notas"
    
    section_title(section)
    
    widths: List[int] = [3, 1]
    chart_column: DeltaGenerator
    card_column: DeltaGenerator
    
    chart_column, card_column = st.columns(widths)
    
    x_column: str = "sessions"
    y_column: str = "grade"
    chart_title: str = "Notas vs. sesiones"
    x_title: str = "Sesiones"
    y_title: str = "Nota"
    
    figure: go.Figure = scatter_with_trend(points, trend, x_column, y_column, chart_title, x_title, y_title)
    
    with chart_column:
        show_figure(figure)
    with card_column:
        kpi_card(card)
    
    interpretation(text)

show()
