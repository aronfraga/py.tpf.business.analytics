from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from data.real_common import (
    load_enrolled_traceability,
    load_enrollment_cross,
    load_grades,
    load_participation,
    sort_by_id_asc,
)
from kpis.kpis_calificaciones import condicion_por_estudiante
from kpis.kpis_cruces import correlacion_participacion_nota, linea_de_tendencia, participacion_vs_notas
from kpis.kpis_participacion import sesiones_por_estudiante
from constants import (
    ACTIVITY_DAYS_LIMIT,
    ALL_KEY,
    ASSOCIATION_DETAIL_TEMPLATE,
    CACHE_TTL_SECONDS,
    CARD_KEY,
    CONDITION_COLUMN,
    CONDITION_LABELS,
    CONDITION_LABEL_FREE,
    CORRELATION_CARD_TITLE,
    DATE_FORMAT,
    DETAIL_KEY,
    DIRECTION_NEGATIVE,
    DIRECTION_POSITIVE,
    ENROLLED_COLUMN,
    FIRST_NAME_COLUMN,
    FULL_NAME_TEMPLATE,
    GRADE_COLUMN,
    GRADE_PERCENT_COLUMN,
    GROUP_COLUMN,
    GROUP_SOURCE_COLUMN,
    INACTIVE_REASON_TEMPLATE,
    LAST_ACTIVITY_TABLE_COLUMN,
    LAST_INTERACTION_COLUMN,
    LAST_NAME_COLUMN,
    MODERATE_LIMIT,
    NEVER_ENTERED_REASON,
    NEVER_LABEL,
    NOT_PRESENTED_LABEL,
    NO_ASSOCIATION_LIMIT,
    PEARSON_COLUMN,
    REASON_SEPARATOR,
    RISK_GRADE_DECIMALS,
    RISK_TABLE_COLUMN,
    SCALE_DIVISOR,
    SCATTER_GRADE_DECIMALS,
    SCATTER_KEY,
    SECONDS_PER_DAY,
    SESSIONS_COLUMN,
    SESSIONS_SOURCE_COLUMN,
    SPINNER_BUILD_CORRELATION,
    STRENGTH_MODERATE,
    STRENGTH_STRONG,
    STRENGTH_VERY_WEAK,
    STRENGTH_WEAK,
    STUDENT_LABEL_TEMPLATE,
    STUDENT_TABLE_COLUMN,
    SUBJECT_ALL,
    SUBJECT_COLUMN,
    SUBJECT_KEYS,
    SUBJECT_OPTIONS,
    TIME_COLUMN,
    TIME_MINUTES_COLUMN,
    TITLE_KEY,
    TREND_KEY,
    USER_COLUMN,
    VALUE_FORMAT,
    VALUE_KEY,
    WEAK_LIMIT,
)

def build_points_table(participation: pd.DataFrame, traceability: pd.DataFrame, grades: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.DataFrame:
    time_and_grades: pd.DataFrame = participacion_vs_notas(participacion=participation, calificaciones=grades, cruce=enrollment_cross)
    sessions: pd.DataFrame = sesiones_por_estudiante(trazabilidad=traceability, cruce=enrollment_cross)
    pair_columns: list = [SUBJECT_COLUMN, USER_COLUMN]
    result: pd.DataFrame = time_and_grades.merge(sessions, on=pair_columns, how="left")

    return result

def scale_grades(percent_values: pd.Series) -> List[float]:
    scaled: pd.Series = percent_values / SCALE_DIVISOR
    rounded: pd.Series = scaled.round(SCATTER_GRADE_DECIMALS)
    result: List[float] = rounded.tolist()

    return result

def build_xy_table(source: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = source[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = source.loc[is_subject]
    times: List[float] = selected[TIME_MINUTES_COLUMN].tolist()
    grades: List[float] = scale_grades(percent_values=selected[GRADE_PERCENT_COLUMN])
    table_data: Dict[str, list] = {
        TIME_COLUMN: times,
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
    times: List[float] = selected[TIME_MINUTES_COLUMN].tolist()
    grades: List[float] = scale_grades(percent_values=selected[GRADE_PERCENT_COLUMN])
    groups: List[str] = selected[GROUP_SOURCE_COLUMN].tolist()
    table_data: Dict[str, list] = {
        TIME_COLUMN: times,
        GRADE_COLUMN: grades,
        GROUP_COLUMN: groups,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_risk_reason(group: str, last_interaction: Any, cutoff: pd.Timestamp) -> str:
    reasons: List[str] = []

    if group == CONDITION_LABEL_FREE:
        reasons.append(CONDITION_LABEL_FREE)

    if group == NOT_PRESENTED_LABEL:
        reasons.append(NOT_PRESENTED_LABEL)

    if pd.isna(last_interaction):
        reasons.append(NEVER_ENTERED_REASON)
    else:
        elapsed: pd.Timedelta = cutoff - last_interaction
        elapsed_days: float = elapsed.total_seconds() / SECONDS_PER_DAY

        if elapsed_days > ACTIVITY_DAYS_LIMIT:
            reasons.append(INACTIVE_REASON_TEMPLATE.format(days=ACTIVITY_DAYS_LIMIT))

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
            student_label: str = STUDENT_LABEL_TEMPLATE.format(user=user, full_name=FULL_NAME_TEMPLATE.format(last_name=last_name, first_name=first_name))
            session_count: int = int(getattr(row, SESSIONS_SOURCE_COLUMN))
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
        STUDENT_TABLE_COLUMN: students,
        RISK_TABLE_COLUMN: risks,
        SESSIONS_COLUMN: sessions,
        GRADE_COLUMN: grades,
        LAST_ACTIVITY_TABLE_COLUMN: last_activities,
    }
    table: pd.DataFrame = pd.DataFrame(table_data)
    sort_columns: List[str] = [SESSIONS_COLUMN, STUDENT_TABLE_COLUMN]
    result: pd.DataFrame = table.sort_values(by=sort_columns).reset_index(drop=True)

    return result

def describe_strength(value: float) -> str:
    magnitude: float = abs(value)
    strength: str

    if magnitude < NO_ASSOCIATION_LIMIT:
        strength = STRENGTH_VERY_WEAK
    elif magnitude < WEAK_LIMIT:
        strength = STRENGTH_WEAK
    elif magnitude < MODERATE_LIMIT:
        strength = STRENGTH_MODERATE
    else:
        strength = STRENGTH_STRONG

    return strength

def describe_direction(value: float) -> str:
    direction: str

    if value >= 0:
        direction = DIRECTION_POSITIVE
    else:
        direction = DIRECTION_NEGATIVE

    return direction

def build_card(correlations: pd.DataFrame, subject: str) -> Dict[str, str]:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = correlations[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = correlations.loc[is_subject]
    pearson: float = float(selected[PEARSON_COLUMN].iloc[0])
    value_text: str = format(pearson, VALUE_FORMAT)
    direction: str = describe_direction(value=pearson)
    strength: str = describe_strength(value=pearson)
    detail: str = ASSOCIATION_DETAIL_TEMPLATE.format(direction=direction, strength=strength)
    result: Dict[str, str] = {TITLE_KEY: CORRELATION_CARD_TITLE, VALUE_KEY: value_text, DETAIL_KEY: detail}

    return result

def add_pooled_rows(table: pd.DataFrame) -> pd.DataFrame:
    pooled: pd.DataFrame = table.assign(**{SUBJECT_COLUMN: ALL_KEY})
    result: pd.DataFrame = pd.concat([table, pooled], ignore_index=True)

    return result

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_BUILD_CORRELATION)
def build_all() -> Dict[str, Dict[str, object]]:
    traceability: pd.DataFrame = load_enrolled_traceability()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    participation: pd.DataFrame = load_participation()
    points_table: pd.DataFrame = build_points_table(
        participation=participation,
        traceability=traceability,
        grades=grades,
        enrollment_cross=enrollment_cross,
    )
    pooled_points: pd.DataFrame = add_pooled_rows(points_table)
    correlations: pd.DataFrame = correlacion_participacion_nota(tabla=pooled_points)
    trend_table: pd.DataFrame = linea_de_tendencia(tabla=pooled_points)
    conditions: Dict[Tuple[str, str], str] = build_conditions(grades=grades, enrollment_cross=enrollment_cross)
    grouped_points: pd.DataFrame = add_groups(points_table=points_table, conditions=conditions)
    participation_index: Dict[Tuple[str, str], Any] = index_participation(participation=participation)
    cutoff: pd.Timestamp = find_cutoff(participation=participation, enrollment_cross=enrollment_cross)
    scatter: Dict[str, pd.DataFrame] = {}
    trend: Dict[str, pd.DataFrame] = {}
    cards: Dict[str, Dict[str, str]] = {}
    risks: Dict[str, pd.DataFrame] = {}

    pooled_grouped: pd.DataFrame = add_pooled_rows(grouped_points)

    for subject in SUBJECT_OPTIONS:
        scatter[subject] = build_scatter_table(source=pooled_grouped, subject=subject)
        trend[subject] = build_xy_table(source=trend_table, subject=subject)
        cards[subject] = build_card(correlations=correlations, subject=subject)

        if subject != SUBJECT_ALL:
            risks[subject] = build_risk_table(grouped_points=grouped_points, participation_index=participation_index, cutoff=cutoff, subject=subject)

    all_risks: pd.DataFrame = pd.concat(list(risks.values()), ignore_index=True)
    risks[SUBJECT_ALL] = all_risks

    for subject_name in list(risks.keys()):
        risks[subject_name] = sort_by_id_asc(risks[subject_name], STUDENT_TABLE_COLUMN)

    result: Dict[str, Dict[str, object]] = {
        SCATTER_KEY: scatter,
        TREND_KEY: trend,
        CARD_KEY: cards,
        RISK_TABLE_COLUMN: risks,
    }

    return result
