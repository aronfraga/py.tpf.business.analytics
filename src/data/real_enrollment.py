from typing import Any, Dict, List, Tuple

import pandas as pd

from data.real_common import (
    ALGEBRA,
    ALGORITHMS,
    PROBABILITY,
    SUBJECT_KEYS,
    SUBJECTS,
    load_all_traceability,
    load_enrollment_cross,
    load_enrollment_list,
    load_participation,
)
from kpis.kpis_matricula import estudiantes_activos, resumen_activos_por_matricula

SUBJECT_COLUMN: str = "materia"
USER_COLUMN: str = "usuario"
ENROLLED_COLUMN: str = "matriculado"
ENTRY_COLUMN: str = "es_ingreso"
INTERACTIONS_COLUMN: str = "interacciones"
LAST_INTERACTION_COLUMN: str = "ultima_interaccion"
LAST_NAME_COLUMN: str = "apellido"
FIRST_NAME_COLUMN: str = "nombre"
ENROLLMENT_DATE_COLUMN: str = "fecha_inscripcion"
ENROLLED_ACTIVE_COLUMN: str = "matriculados_activos"
NOT_ENROLLED_ACTIVE_COLUMN: str = "no_matriculados_activos"
FLAG_NOT_ENROLLED_ACTIVE: str = "activo_no_inscripto"
FLAG_ACTIVE_WITH_DROP: str = "activo_con_baja"
FLAG_ENROLLED_WITHOUT_ACTIVITY: str = "inscripto_sin_actividad"

DATE_FORMAT: str = "%Y-%m-%d"
NEVER_TEXT: str = "Nunca"

ALERT_ACTIVE_WITH_DROP: str = "Activo con baja"
ALERT_NO_ENTRIES: str = "Sin ingresos"
ALERT_NOT_ENROLLED_ACTIVE: str = "No inscripto activo"

NOT_ENROLLED_ACTIVE_LABELS: Dict[str, str] = {
    "user": "Usuario",
    "sessions": "Sesiones",
    "last_activity": "Última actividad",
}

ENROLLED_NO_PARTICIPATION_LABELS: Dict[str, str] = {
    "student": "Estudiante",
    "enrollment_date": "Fecha de inscripción",
    "last_access": "Último acceso",
}

ALERTS_LABELS: Dict[str, str] = {
    "student": "Estudiante",
    "alert": "Alerta",
    "detail": "Detalle",
}

def format_date(moment: pd.Timestamp) -> str:
    text: str = moment.strftime(DATE_FORMAT)

    return text

def index_participation(participation: pd.DataFrame) -> Dict[Tuple[str, str], Any]:
    index: Dict[Tuple[str, str], Any] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        index[pair] = row

    return index

def index_enrollment_dates(enrollment_list: pd.DataFrame) -> Dict[Tuple[str, str], pd.Timestamp]:
    dates: Dict[Tuple[str, str], pd.Timestamp] = {}

    for row in enrollment_list.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        moment: pd.Timestamp = getattr(row, ENROLLMENT_DATE_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        dates[pair] = moment

    return dates

def index_sessions(traceability: pd.DataFrame) -> Dict[Tuple[str, str], int]:
    sessions: Dict[Tuple[str, str], int] = {}
    grouped: pd.core.groupby.DataFrameGroupBy = traceability.groupby([SUBJECT_COLUMN, USER_COLUMN])
    counts: pd.Series = grouped[ENTRY_COLUMN].sum()

    for key, value in counts.items():
        subject_key: str = key[0]
        user: str = key[1]
        pair: Tuple[str, str] = (subject_key, user)
        sessions[pair] = int(value)

    return sessions

def select_users(cross: pd.DataFrame, flag_column: str, subject_key: str) -> List[str]:
    has_flag: pd.Series = cross[flag_column]
    is_subject: pd.Series = cross[SUBJECT_COLUMN] == subject_key
    mask: pd.Series = has_flag & is_subject
    selected: pd.DataFrame = cross.loc[mask]
    users: List[str] = sorted(selected[USER_COLUMN].tolist())

    return users

def build_student_label(user: str, participation_row: Any) -> str:
    last_name: str = getattr(participation_row, LAST_NAME_COLUMN)
    first_name: str = getattr(participation_row, FIRST_NAME_COLUMN)
    label: str = f"{user} – {last_name}, {first_name}"

    return label

def build_not_enrolled_table(users: List[str], subject_key: str, participation_index: Dict[Tuple[str, str], Any], sessions: Dict[Tuple[str, str], int]) -> pd.DataFrame:
    user_values: List[str] = []
    session_values: List[int] = []
    last_activity_values: List[str] = []

    for user in users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        last_interaction: pd.Timestamp = getattr(participation_row, LAST_INTERACTION_COLUMN)
        user_values.append(user)
        session_values.append(sessions.get(pair, 0))
        last_activity_values.append(format_date(moment=last_interaction))

    table_data: Dict[str, list] = {
        "user": user_values,
        "sessions": session_values,
        "last_activity": last_activity_values,
    }
    table: pd.DataFrame = pd.DataFrame(table_data)
    sort_columns: List[str] = ["sessions", "user"]
    sort_order: List[bool] = [False, True]
    result: pd.DataFrame = table.sort_values(by=sort_columns, ascending=sort_order).reset_index(drop=True)

    return result

def build_no_participation_table(users: List[str], subject_key: str, participation_index: Dict[Tuple[str, str], Any], enrollment_dates: Dict[Tuple[str, str], pd.Timestamp]) -> pd.DataFrame:
    students: List[str] = []
    dates: List[str] = []
    last_access: List[str] = []

    for user in users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        student_label: str = build_student_label(user=user, participation_row=participation_row)
        enrollment_moment: pd.Timestamp = enrollment_dates[pair]
        students.append(student_label)
        dates.append(format_date(moment=enrollment_moment))
        last_access.append(NEVER_TEXT)

    table_data: Dict[str, list] = {
        "student": students,
        "enrollment_date": dates,
        "last_access": last_access,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_alerts_table(cross: pd.DataFrame, subject_key: str, participation_index: Dict[Tuple[str, str], Any], sessions: Dict[Tuple[str, str], int]) -> pd.DataFrame:
    students: List[str] = []
    alerts: List[str] = []
    details: List[str] = []
    drop_users: List[str] = select_users(cross=cross, flag_column=FLAG_ACTIVE_WITH_DROP, subject_key=subject_key)
    no_entry_users: List[str] = select_users(cross=cross, flag_column=FLAG_ENROLLED_WITHOUT_ACTIVITY, subject_key=subject_key)
    not_enrolled_users: List[str] = select_users(cross=cross, flag_column=FLAG_NOT_ENROLLED_ACTIVE, subject_key=subject_key)

    for user in drop_users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        interactions: int = int(getattr(participation_row, INTERACTIONS_COLUMN))
        last_text: str = format_date(moment=getattr(participation_row, LAST_INTERACTION_COLUMN))
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(ALERT_ACTIVE_WITH_DROP)
        details.append(f"Inscripción en estado Baja con {interactions} interacciones; última actividad {last_text}")

    for user in no_entry_users:
        pair = (subject_key, user)
        participation_row = participation_index[pair]
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(ALERT_NO_ENTRIES)
        details.append("Inscripción sin ningún ingreso")

    for user in not_enrolled_users:
        pair = (subject_key, user)
        participation_row = participation_index[pair]
        session_count: int = sessions.get(pair, 0)
        last_text = format_date(moment=getattr(participation_row, LAST_INTERACTION_COLUMN))
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(ALERT_NOT_ENROLLED_ACTIVE)
        details.append(f"No figura en la matrícula; {session_count} sesiones, última actividad {last_text}")

    table_data: Dict[str, list] = {
        "student": students,
        "alert": alerts,
        "detail": details,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def select_summary_row(summary: pd.DataFrame, subject_key: str) -> pd.Series:
    is_subject: pd.Series = summary[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = summary.loc[is_subject]
    row: pd.Series = selected.iloc[0]

    return row

def build_cards(enrolled_count: int, enrolled_active: int, not_enrolled_active: int, no_participation: int, alerts_count: int) -> List[Dict[str, str]]:
    cards: List[Dict[str, str]] = [
        {"title": "Matriculados", "value": str(enrolled_count), "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": str(enrolled_active), "detail": "Con actividad registrada"},
        {"title": "No inscriptos activos", "value": str(not_enrolled_active), "detail": "Usuarios sin matrícula"},
        {"title": "Inscriptos sin participación", "value": str(no_participation), "detail": "Nunca ingresaron"},
        {"title": "Alertas", "value": str(alerts_count), "detail": "Estudiantes a revisar"},
    ]

    return cards

def build_enrolled_vs_active(enrolled_count: int, enrolled_active: int) -> pd.DataFrame:
    table_data: Dict[str, list] = {
        "status": ["Matriculados", "Activos"],
        "count": [enrolled_count, enrolled_active],
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_all() -> Dict[str, Dict[str, Any]]:
    participation: pd.DataFrame = load_participation()
    cross: pd.DataFrame = load_enrollment_cross()
    enrollment_list: pd.DataFrame = load_enrollment_list()
    traceability: pd.DataFrame = load_all_traceability()
    participation_index: Dict[Tuple[str, str], Any] = index_participation(participation=participation)
    enrollment_dates: Dict[Tuple[str, str], pd.Timestamp] = index_enrollment_dates(enrollment_list=enrollment_list)
    sessions: Dict[Tuple[str, str], int] = index_sessions(traceability=traceability)
    active_students: pd.DataFrame = estudiantes_activos(participacion=participation, cruce=cross)
    summary: pd.DataFrame = resumen_activos_por_matricula(activos=active_students)
    cards: Dict[str, List[Dict[str, str]]] = {}
    enrolled_vs_active: Dict[str, pd.DataFrame] = {}
    not_enrolled: Dict[str, pd.DataFrame] = {}
    no_participation: Dict[str, pd.DataFrame] = {}
    alerts: Dict[str, pd.DataFrame] = {}

    for subject in SUBJECTS:
        subject_key: str = SUBJECT_KEYS[subject]
        summary_row: pd.Series = select_summary_row(summary=summary, subject_key=subject_key)
        enrolled_users: List[str] = select_users(cross=cross, flag_column=ENROLLED_COLUMN, subject_key=subject_key)
        not_enrolled_users: List[str] = select_users(cross=cross, flag_column=FLAG_NOT_ENROLLED_ACTIVE, subject_key=subject_key)
        no_participation_users: List[str] = select_users(cross=cross, flag_column=FLAG_ENROLLED_WITHOUT_ACTIVITY, subject_key=subject_key)
        not_enrolled[subject] = build_not_enrolled_table(users=not_enrolled_users, subject_key=subject_key, participation_index=participation_index, sessions=sessions)
        no_participation[subject] = build_no_participation_table(users=no_participation_users, subject_key=subject_key, participation_index=participation_index, enrollment_dates=enrollment_dates)
        alerts[subject] = build_alerts_table(cross=cross, subject_key=subject_key, participation_index=participation_index, sessions=sessions)
        enrolled_count: int = len(enrolled_users)
        enrolled_active_count: int = int(summary_row[ENROLLED_ACTIVE_COLUMN])
        not_enrolled_active_count: int = int(summary_row[NOT_ENROLLED_ACTIVE_COLUMN])
        alerts_count: int = len(alerts[subject])
        cards[subject] = build_cards(
            enrolled_count=enrolled_count,
            enrolled_active=enrolled_active_count,
            not_enrolled_active=not_enrolled_active_count,
            no_participation=len(no_participation_users),
            alerts_count=alerts_count,
        )
        enrolled_vs_active[subject] = build_enrolled_vs_active(enrolled_count=enrolled_count, enrolled_active=enrolled_active_count)

    result: Dict[str, Dict[str, Any]] = {
        "cards": cards,
        "enrolled_vs_active": enrolled_vs_active,
        "not_enrolled": not_enrolled,
        "no_participation": no_participation,
        "alerts": alerts,
    }

    return result

ALL_TABLES: Dict[str, Dict[str, Any]] = build_all()

ENROLLMENT_KPIS: Dict[str, List[Dict[str, str]]] = ALL_TABLES["cards"]

ENROLLED_VS_ACTIVE: Dict[str, pd.DataFrame] = ALL_TABLES["enrolled_vs_active"]

NOT_ENROLLED_ACTIVE: Dict[str, pd.DataFrame] = ALL_TABLES["not_enrolled"]

ENROLLED_NO_PARTICIPATION: Dict[str, pd.DataFrame] = ALL_TABLES["no_participation"]

ALERTS: Dict[str, pd.DataFrame] = ALL_TABLES["alerts"]

ENROLLMENT_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "Ocho de cada diez matriculados están activos. Hay usuarios con actividad que "
        "no figuran en la matrícula y estudiantes inscriptos que nunca ingresaron."
    ),
    ALGORITHMS: (
        "Es la asignatura con más matriculados y la mayor cantidad de estudiantes "
        "inactivos en términos absolutos. Las alertas combinan abandono e "
        "inscripciones sin ingresos."
    ),
    PROBABILITY: (
        "Presenta la menor proporción de estudiantes activos sobre la matrícula. "
        "Todas las alertas corresponden a abandono o falta de ingresos."
    ),
}
