from typing import Any, Dict, List
from data.services.real_enrollment import build_all
from ui.components.cards import card_row
from ui.components.filters import selector
from ui.components.tables import table
from ui.components.texts import section_title
import pandas as pd
import streamlit as st
import constants as const

ALERT_DETAILS: Dict[str, str] = {
    const.ALERT_ACTIVE_WITH_DROP: "Inscripciones",
    const.ALERT_NO_ENTRIES: "Inscripciones",
    const.ALERT_NOT_ENROLLED_ACTIVE: "Usuarios por asignatura",
}

def show() -> None:
    page_title: str = "Matrícula y Alertas"
    st.title(page_title)

    tables: Dict[str, Dict[str, Any]] = build_all()

    subject_label: str = "Asignatura"
    subject_key: str = "enrollment_subject"
    subject: str = selector(subject_label, const.SUBJECT_OPTIONS, subject_key)
    cards: List[Dict[str, str]] = tables["cards"][subject]
    not_enrolled: pd.DataFrame = tables["not_enrolled"][subject]
    no_participation: pd.DataFrame = tables["no_participation"][subject]
    alerts: pd.DataFrame = tables["alerts"][subject]
    card_row(cards)

    if subject == const.SUBJECT_ALL:
        all_note: str = "En \"Todas las asignaturas\" las cifras cuentan inscripciones: un alumno inscripto en varias asignaturas se cuenta una vez por cada una."
        st.caption(all_note)

    detail_section: str = "Detalle"
    section_title(detail_section)
    
    not_enrolled_title: str = "No inscriptos con alguna actividad"
    no_participation_title: str = "Inscriptos sin participación"
    
    table(not_enrolled, not_enrolled_title, const.NOT_ENROLLED_ACTIVE_LABELS)
    table(no_participation, no_participation_title, const.ENROLLED_NO_PARTICIPATION_LABELS)
    
    alerts_section: str = "Alertas"
    section_title(alerts_section)
    
    alert_types: List[str] = [const.ALERT_ACTIVE_WITH_DROP, const.ALERT_NO_ENTRIES, const.ALERT_NOT_ENROLLED_ACTIVE]
    alert_cards: List[Dict[str, str]] = []

    for alert_type in alert_types:
        type_count: int = int((alerts["alert"] == alert_type).sum())
        alert_cards.append({"title": alert_type, "value": str(type_count), "detail": ALERT_DETAILS[alert_type]})

    total_card: Dict[str, str] = {"title": "Total de alertas", "value": str(len(alerts)), "detail": "Suma de las alertas (inscripciones)"}
    alert_cards.append(total_card)
    card_row(alert_cards)

    alerts_title: str = "Alertas de la asignatura"
    table(alerts, alerts_title, const.ALERTS_LABELS)

show()
