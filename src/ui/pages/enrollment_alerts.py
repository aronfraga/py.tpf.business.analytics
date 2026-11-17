from typing import Dict, List
import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from data.real_common import SUBJECT_OPTIONS
from data.real_enrollment import ALERT_ACTIVE_WITH_DROP, ALERT_NO_ENTRIES, ALERT_NOT_ENROLLED_ACTIVE, ALERTS,ALERTS_LABELS, ENROLLED_NO_PARTICIPATION, ENROLLED_NO_PARTICIPATION_LABELS, ENROLLMENT_KPIS, NOT_ENROLLED_ACTIVE, NOT_ENROLLED_ACTIVE_LABELS
from ui.components.cards import card_row
from ui.components.filters import selector
from ui.components.tables import table
from ui.components.texts import section_title

def show() -> None:
    page_title: str = "Matrícula y Alertas"
    st.title(page_title)
    
    subject_label: str = "Asignatura"
    subject_key: str = "enrollment_subject"
    subject: str = selector(subject_label, SUBJECT_OPTIONS, subject_key)
    cards: List[Dict[str, str]] = ENROLLMENT_KPIS[subject]
    not_enrolled: pd.DataFrame = NOT_ENROLLED_ACTIVE[subject]
    no_participation: pd.DataFrame = ENROLLED_NO_PARTICIPATION[subject]
    alerts: pd.DataFrame = ALERTS[subject]
    card_row(cards)
    
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
    
    alert_types: List[str] = [ALERT_ACTIVE_WITH_DROP, ALERT_NO_ENTRIES, ALERT_NOT_ENROLLED_ACTIVE]
    alert_cards: List[Dict[str, str]] = []

    for alert_type in alert_types:
        type_count: int = int((alerts["alert"] == alert_type).sum())
        alert_cards.append({"title": alert_type, "value": str(type_count), "detail": "Estudiantes"})

    total_card: Dict[str, str] = {"title": "Total de alertas", "value": str(len(alerts)), "detail": "Suma de todas las alertas"}
    alert_cards.append(total_card)
    card_row(alert_cards)

    alerts_title: str = "Alertas de la asignatura"
    table(alerts, alerts_title, ALERTS_LABELS)

show()
