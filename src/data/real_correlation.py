from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from data.real_common import (
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrolled_traceability,
    load_enrollment_cross,
    load_grades,
    load_participation,
)
from kpis.kpis_calificaciones import condicion_por_estudiante, nota_por_estudiante
from kpis.kpis_cruces import correlacion_participacion_nota, linea_de_tendencia
from kpis.kpis_participacion import DIAS_ACTIVIDAD, sesiones_por_estudiante

SUBJECT_COLUMN: str = "materia"
USER_COLUMN: str = "usuario"
SESSIONS_SOURCE_COLUMN: str = "sesiones"
KPI_X_COLUMN: str = "tiempo_min"
GRADE_PERCENT_COLUMN: str = "nota_pct"
PRESENTED_COLUMN: str = "se_presento"
PEARSON_COLUMN: str = "pearson"
SESSIONS_COLUMN: str = "sessions"
GRADE_COLUMN: str = "grade"
GROUP_SOURCE_COLUMN: str = "grupo"
GROUP_COLUMN: str = "group"
CONDITION_COLUMN: str = "condicion"
ENROLLED_COLUMN: str = "matriculado"
LAST_INTERACTION_COLUMN: str = "ultima_interaccion"
LAST_NAME_COLUMN: str = "apellido"
FIRST_NAME_COLUMN: str = "nombre"

CONDITION_LABELS: Dict[str, str] = {
    "promocionado": "Promociona",
    "regular": "Regular",
    "libre": "Libre",
}

LIBRE_LABEL: str = "Libre"
NOT_PRESENTED_LABEL: str = "No se presentó"
NEVER_LABEL: str = "Nunca"
NEVER_ENTERED_REASON: str = "Nunca ingresó"
INACTIVE_REASON: str = "Sin actividad hace más de 15 días"
REASON_SEPARATOR: str = "; "
DATE_FORMAT: str = "%Y-%m-%d"
SECONDS_PER_DAY: float = 86400.0
RISK_GRADE_DECIMALS: int = 1

RISK_LABELS: Dict[str, str] = {
    "student": "Estudiante",
    "risk": "Motivo",
    "sessions": "Sesiones",
    "grade": "Nota",
    "last_activity": "Última actividad",
}

SCALE_DIVISOR: int = 10
GRADE_DECIMALS: int = 2
VALUE_FORMAT: str = ".2f"
CARD_TITLE: str = "Correlación sesiones–nota"

NO_ASSOCIATION_LIMIT: float = 0.1
WEAK_LIMIT: float = 0.3
MODERATE_LIMIT: float = 0.5

def build_points_table(traceability: pd.DataFrame, grades: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.DataFrame:
    sessions: pd.DataFrame = sesiones_por_estudiante(trazabilidad=traceability, cruce=enrollment_cross)
    student_grades: pd.DataFrame = nota_por_estudiante(calificaciones=grades)
    pair_columns: list = [SUBJECT_COLUMN, USER_COLUMN]
    grade_columns: list = [SUBJECT_COLUMN, USER_COLUMN, GRADE_PERCENT_COLUMN]
    selected_grades: pd.DataFrame = student_grades[grade_columns]
    merged: pd.DataFrame = sessions.merge(selected_grades, on=pair_columns, how="left")
    merged[PRESENTED_COLUMN] = merged[GRADE_PERCENT_COLUMN].notna()
    filled_grades: pd.Series = merged[GRADE_PERCENT_COLUMN].fillna(0)
    merged[GRADE_PERCENT_COLUMN] = filled_grades
    rename_map: Dict[str, str] = {SESSIONS_SOURCE_COLUMN: KPI_X_COLUMN}
    result: pd.DataFrame = merged.rename(columns=rename_map)

    return result

def scale_grades(percent_values: pd.Series) -> List[float]:
    scaled: pd.Series = percent_values / SCALE_DIVISOR
    rounded: pd.Series = scaled.round(GRADE_DECIMALS)
    result: List[float] = rounded.tolist()

    return result

def build_xy_table(source: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = source[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = source.loc[is_subject]
    sessions: List[float] = selected[KPI_X_COLUMN].tolist()
    grades: List[float] = scale_grades(percent_values=selected[GRADE_PERCENT_COLUMN])
    table_data: Dict[str, list] = {
        SESSIONS_COLUMN: sessions,
        GRADE_COLUMN: grades,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_conditions(grades: pd.DataFrame, enrollment_cross: pd.DataFrame) -> Dict[Tuple[str, str], str]:
    conditions_table: pd.DataFrame = condicion_por_estudiante(calificaciones=grades, cruce=enrollment_cross, matriculados=True)
    conditions: Dict[Tuple[str, str], str] = {}

    for row in conditions_table.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        condition: str = getattr(row, CONDITION_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        conditions[pair] = CONDITION_LABELS[condition]

    return conditions

def add_groups(points_table: pd.DataFrame, conditions: Dict[Tuple[str, str], str]) -> pd.DataFrame:
    groups: List[str] = []

    for row in points_table.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        group: str = conditions.get(pair, NOT_PRESENTED_LABEL)
        groups.append(group)

    result: pd.DataFrame = points_table.copy()
    result[GROUP_SOURCE_COLUMN] = groups

    return result

def build_scatter_table(source: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = source[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = source.loc[is_subject]
    sessions: List[float] = selected[KPI_X_COLUMN].tolist()
    grades: List[float] = scale_grades(percent_values=selected[GRADE_PERCENT_COLUMN])
    groups: List[str] = selected[GROUP_SOURCE_COLUMN].tolist()
    table_data: Dict[str, list] = {
        SESSIONS_COLUMN: sessions,
        GRADE_COLUMN: grades,
        GROUP_COLUMN: groups,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_risk_reason(group: str, last_interaction: Any, cutoff: pd.Timestamp) -> str:
    reasons: List[str] = []

    if group == LIBRE_LABEL:
        reasons.append(LIBRE_LABEL)

    if group == NOT_PRESENTED_LABEL:
        reasons.append(NOT_PRESENTED_LABEL)

    if pd.isna(last_interaction):
        reasons.append(NEVER_ENTERED_REASON)
    else:
        elapsed: pd.Timedelta = cutoff - last_interaction
        elapsed_days: float = elapsed.total_seconds() / SECONDS_PER_DAY

        if elapsed_days > DIAS_ACTIVIDAD:
            reasons.append(INACTIVE_REASON)

    text: str = REASON_SEPARATOR.join(reasons)

    return text

def index_participation(participation: pd.DataFrame) -> Dict[Tuple[str, str], Any]:
    index: Dict[Tuple[str, str], Any] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        index[pair] = row

    return index

def find_cutoff(participation: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.Timestamp:
    pair_columns: list = [SUBJECT_COLUMN, USER_COLUMN]
    is_enrolled: pd.Series = enrollment_cross[ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    enrolled_pairs: pd.DataFrame = enrolled_rows[pair_columns]
    enrolled_participation: pd.DataFrame = participation.merge(enrolled_pairs, on=pair_columns, how="inner")
    cutoff: pd.Timestamp = enrolled_participation[LAST_INTERACTION_COLUMN].max()

    return cutoff

def build_risk_table(grouped_points: pd.DataFrame, participation_index: Dict[Tuple[str, str], Any], cutoff: pd.Timestamp, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = grouped_points[SUBJECT_COLUMN] == subject_key
    subject_rows: pd.DataFrame = grouped_points.loc[is_subject]
    students: List[str] = []
    risks: List[str] = []
    sessions: List[int] = []
    grades: List[Optional[float]] = []
    last_activities: List[str] = []

    for row in subject_rows.itertuples(index=False):
        user: str = getattr(row, USER_COLUMN)
        group: str = getattr(row, GROUP_SOURCE_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        last_interaction: Any = getattr(participation_row, LAST_INTERACTION_COLUMN)
        reason: str = build_risk_reason(group=group, last_interaction=last_interaction, cutoff=cutoff)

        if reason != "":
            last_name: str = getattr(participation_row, LAST_NAME_COLUMN)
            first_name: str = getattr(participation_row, FIRST_NAME_COLUMN)
            student_label: str = f"{user} – {last_name}, {first_name}"
            session_count: int = int(getattr(row, KPI_X_COLUMN))
            grade_value: Optional[float]
            last_text: str

            if group == NOT_PRESENTED_LABEL:
                grade_value = None
            else:
                percent: float = float(getattr(row, GRADE_PERCENT_COLUMN))
                grade_value = round(percent / SCALE_DIVISOR, RISK_GRADE_DECIMALS)

            if pd.isna(last_interaction):
                last_text = NEVER_LABEL
            else:
                last_text = last_interaction.strftime(DATE_FORMAT)

            students.append(student_label)
            risks.append(reason)
            sessions.append(session_count)
            grades.append(grade_value)
            last_activities.append(last_text)

    table_data: Dict[str, list] = {
        "student": students,
        "risk": risks,
        "sessions": sessions,
        "grade": grades,
        "last_activity": last_activities,
    }
    table: pd.DataFrame = pd.DataFrame(table_data)
    sort_columns: List[str] = ["sessions", "student"]
    result: pd.DataFrame = table.sort_values(by=sort_columns).reset_index(drop=True)

    return result

def describe_strength(value: float) -> str:
    magnitude: float = abs(value)
    strength: str

    if magnitude < NO_ASSOCIATION_LIMIT:
        strength = "muy débil"
    elif magnitude < WEAK_LIMIT:
        strength = "débil"
    elif magnitude < MODERATE_LIMIT:
        strength = "moderada"
    else:
        strength = "fuerte"

    return strength

def describe_direction(value: float) -> str:
    direction: str

    if value >= 0:
        direction = "positiva"
    else:
        direction = "negativa"

    return direction

def build_card(correlations: pd.DataFrame, subject: str) -> Dict[str, str]:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = correlations[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = correlations.loc[is_subject]
    pearson: float = float(selected[PEARSON_COLUMN].iloc[0])
    value_text: str = format(pearson, VALUE_FORMAT)
    direction: str = describe_direction(value=pearson)
    strength: str = describe_strength(value=pearson)
    detail: str = f"Asociación {direction} {strength}"
    result: Dict[str, str] = {"title": CARD_TITLE, "value": value_text, "detail": detail}

    return result

def build_all() -> Dict[str, Dict[str, object]]:
    traceability: pd.DataFrame = load_enrolled_traceability()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    points_table: pd.DataFrame = build_points_table(
        traceability=traceability,
        grades=grades,
        enrollment_cross=enrollment_cross,
    )
    correlations: pd.DataFrame = correlacion_participacion_nota(tabla=points_table)
    trend_table: pd.DataFrame = linea_de_tendencia(tabla=points_table)
    participation: pd.DataFrame = load_participation()
    conditions: Dict[Tuple[str, str], str] = build_conditions(grades=grades, enrollment_cross=enrollment_cross)
    grouped_points: pd.DataFrame = add_groups(points_table=points_table, conditions=conditions)
    participation_index: Dict[Tuple[str, str], Any] = index_participation(participation=participation)
    cutoff: pd.Timestamp = find_cutoff(participation=participation, enrollment_cross=enrollment_cross)
    scatter: Dict[str, pd.DataFrame] = {}
    trend: Dict[str, pd.DataFrame] = {}
    cards: Dict[str, Dict[str, str]] = {}
    risks: Dict[str, pd.DataFrame] = {}

    for subject in SUBJECTS:
        scatter[subject] = build_scatter_table(source=grouped_points, subject=subject)
        trend[subject] = build_xy_table(source=trend_table, subject=subject)
        cards[subject] = build_card(correlations=correlations, subject=subject)
        risks[subject] = build_risk_table(grouped_points=grouped_points, participation_index=participation_index, cutoff=cutoff, subject=subject)

    result: Dict[str, Dict[str, object]] = {
        "scatter": scatter,
        "trend": trend,
        "card": cards,
        "risk": risks,
    }

    return result

ALL_TABLES: Dict[str, Dict[str, object]] = build_all()

SCATTER: Dict[str, pd.DataFrame] = ALL_TABLES["scatter"]

TREND_LINE: Dict[str, pd.DataFrame] = ALL_TABLES["trend"]

CORRELATION: Dict[str, Dict[str, str]] = ALL_TABLES["card"]

RISK_STUDENTS: Dict[str, pd.DataFrame] = ALL_TABLES["risk"]
