from typing import Any, Dict, List, Optional, Tuple
from data.services.real_common import (load_enrolled_traceability, load_enrollment_cross, load_grades, load_participation, sort_by_id_asc)
from data.kpis.kpis_calificaciones import condicion_por_estudiante
from data.kpis.kpis_cruces import correlacion_participacion_nota, linea_de_tendencia, participacion_vs_notas
from data.kpis.kpis_participacion import sesiones_por_estudiante
import pandas as pd
import streamlit as st
import constants as const

def build_points_table(participation: pd.DataFrame, traceability: pd.DataFrame, grades: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.DataFrame:
    time_and_grades: pd.DataFrame = participacion_vs_notas(
        participacion=participation, calificaciones=grades, cruce=enrollment_cross)
    sessions: pd.DataFrame = sesiones_por_estudiante(trazabilidad=traceability, cruce=enrollment_cross)
    pair_columns: list = [const.SUBJECT_COLUMN, const.USER_COLUMN]
    result: pd.DataFrame = time_and_grades.merge(sessions, on=pair_columns, how="left")

    return result

def scale_grades(percent_values: pd.Series) -> List[float]:
    scaled: pd.Series = percent_values / const.SCALE_DIVISOR
    rounded: pd.Series = scaled.round(const.SCATTER_GRADE_DECIMALS)
    result: List[float] = rounded.tolist()

    return result

def build_xy_table(source: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = source[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = source.loc[is_subject]
    times: List[float] = selected[const.TIME_MINUTES_COLUMN].tolist()
    grades: List[float] = scale_grades(percent_values=selected[const.GRADE_PERCENT_COLUMN])
    table_data: Dict[str, list] = {
        const.TIME_COLUMN: times,
        const.GRADE_COLUMN: grades,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_conditions(grades: pd.DataFrame, enrollment_cross: pd.DataFrame) -> Dict[Tuple[str, str], str]:
    conditions_table: pd.DataFrame = condicion_por_estudiante(
        calificaciones=grades, cruce=enrollment_cross, matriculados=True)
    conditions: Dict[Tuple[str, str], str] = {}

    for row in conditions_table.itertuples(index=False):
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        condition: str = getattr(row, const.CONDITION_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        conditions[pair] = const.CONDITION_LABELS[condition]

    return conditions

def add_groups(points_table: pd.DataFrame, conditions: Dict[Tuple[str, str], str]) -> pd.DataFrame:
    groups: List[str] = []

    for row in points_table.itertuples(index=False):
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        group: str = conditions.get(pair, const.NOT_PRESENTED_LABEL)
        groups.append(group)

    result: pd.DataFrame = points_table.copy()
    result[const.GROUP_SOURCE_COLUMN] = groups

    return result

def build_scatter_table(source: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = source[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = source.loc[is_subject]
    times: List[float] = selected[const.TIME_MINUTES_COLUMN].tolist()
    grades: List[float] = scale_grades(percent_values=selected[const.GRADE_PERCENT_COLUMN])
    groups: List[str] = selected[const.GROUP_SOURCE_COLUMN].tolist()
    table_data: Dict[str, list] = {
        const.TIME_COLUMN: times,
        const.GRADE_COLUMN: grades,
        const.GROUP_COLUMN: groups,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_risk_reason(group: str, last_interaction: Any, cutoff: pd.Timestamp) -> str:
    reasons: List[str] = []

    if group == const.CONDITION_LABEL_FREE:
        reasons.append(const.CONDITION_LABEL_FREE)

    if group == const.NOT_PRESENTED_LABEL:
        reasons.append(const.NOT_PRESENTED_LABEL)

    if pd.isna(last_interaction):
        reasons.append(const.NEVER_ENTERED_REASON)
    else:
        elapsed: pd.Timedelta = cutoff - last_interaction
        elapsed_days: float = elapsed.total_seconds() / const.SECONDS_PER_DAY

        if elapsed_days > const.ACTIVITY_DAYS_LIMIT:
            reasons.append(const.INACTIVE_REASON_TEMPLATE.format(days=const.ACTIVITY_DAYS_LIMIT))

    text: str = const.REASON_SEPARATOR.join(reasons)

    return text

def index_participation(participation: pd.DataFrame) -> Dict[Tuple[str, str], Any]:
    index: Dict[Tuple[str, str], Any] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        index[pair] = row

    return index

def find_cutoff(participation: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.Timestamp:
    pair_columns: list = [const.SUBJECT_COLUMN, const.USER_COLUMN]
    is_enrolled: pd.Series = enrollment_cross[const.ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    enrolled_pairs: pd.DataFrame = enrolled_rows[pair_columns]
    enrolled_participation: pd.DataFrame = participation.merge(enrolled_pairs, on=pair_columns, how="inner")
    cutoff: pd.Timestamp = enrolled_participation[const.LAST_INTERACTION_COLUMN].max()

    return cutoff

def build_risk_table(grouped_points: pd.DataFrame, participation_index: Dict[Tuple[str, str], Any], cutoff: pd.Timestamp, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = grouped_points[const.SUBJECT_COLUMN] == subject_key
    subject_rows: pd.DataFrame = grouped_points.loc[is_subject]
    students: List[str] = []
    risks: List[str] = []
    sessions: List[int] = []
    grades: List[Optional[float]] = []
    last_activities: List[str] = []

    for row in subject_rows.itertuples(index=False):
        user: str = getattr(row, const.USER_COLUMN)
        group: str = getattr(row, const.GROUP_SOURCE_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        last_interaction: Any = getattr(participation_row, const.LAST_INTERACTION_COLUMN)
        reason: str = build_risk_reason(group=group, last_interaction=last_interaction, cutoff=cutoff)

        if reason != "":
            last_name: str = getattr(participation_row, const.LAST_NAME_COLUMN)
            first_name: str = getattr(participation_row, const.FIRST_NAME_COLUMN)
            student_label: str = const.STUDENT_LABEL_TEMPLATE.format(
                user=user, full_name=const.FULL_NAME_TEMPLATE.format(last_name=last_name, first_name=first_name))
            session_count: int = int(getattr(row, const.SESSIONS_SOURCE_COLUMN))
            grade_value: Optional[float]
            last_text: str

            if group == const.NOT_PRESENTED_LABEL:
                grade_value = None
            else:
                percent: float = float(getattr(row, const.GRADE_PERCENT_COLUMN))
                grade_value = round(percent / const.SCALE_DIVISOR, const.RISK_GRADE_DECIMALS)

            if pd.isna(last_interaction):
                last_text = const.NEVER_LABEL
            else:
                last_text = last_interaction.strftime(const.DATE_FORMAT)

            students.append(student_label)
            risks.append(reason)
            sessions.append(session_count)
            grades.append(grade_value)
            last_activities.append(last_text)

    table_data: Dict[str, list] = {
        const.STUDENT_TABLE_COLUMN: students,
        const.RISK_TABLE_COLUMN: risks,
        const.SESSIONS_COLUMN: sessions,
        const.GRADE_COLUMN: grades,
        const.LAST_ACTIVITY_TABLE_COLUMN: last_activities,
    }
    table: pd.DataFrame = pd.DataFrame(table_data)
    sort_columns: List[str] = [const.SESSIONS_COLUMN, const.STUDENT_TABLE_COLUMN]
    result: pd.DataFrame = table.sort_values(by=sort_columns).reset_index(drop=True)

    return result

def describe_strength(value: float) -> str:
    magnitude: float = abs(value)
    strength: str

    if magnitude < const.NO_ASSOCIATION_LIMIT:
        strength = const.STRENGTH_VERY_WEAK
    elif magnitude < const.WEAK_LIMIT:
        strength = const.STRENGTH_WEAK
    elif magnitude < const.MODERATE_LIMIT:
        strength = const.STRENGTH_MODERATE
    else:
        strength = const.STRENGTH_STRONG

    return strength

def describe_direction(value: float) -> str:
    direction: str

    if value >= 0:
        direction = const.DIRECTION_POSITIVE
    else:
        direction = const.DIRECTION_NEGATIVE

    return direction

def build_card(correlations: pd.DataFrame, subject: str) -> Dict[str, str]:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = correlations[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = correlations.loc[is_subject]
    pearson: float = float(selected[const.PEARSON_COLUMN].iloc[0])
    value_text: str = format(pearson, const.VALUE_FORMAT)
    direction: str = describe_direction(value=pearson)
    strength: str = describe_strength(value=pearson)
    detail: str = const.ASSOCIATION_DETAIL_TEMPLATE.format(direction=direction, strength=strength)
    result: Dict[str, str] = {const.TITLE_KEY: const.CORRELATION_CARD_TITLE, const.VALUE_KEY: value_text, const.DETAIL_KEY: detail}

    return result

def add_pooled_rows(table: pd.DataFrame) -> pd.DataFrame:
    pooled: pd.DataFrame = table.assign(**{const.SUBJECT_COLUMN: const.ALL_KEY})
    result: pd.DataFrame = pd.concat([table, pooled], ignore_index=True)

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_CORRELATION)
def build_all() -> Dict[str, Dict[str, object]]:
    traceability: pd.DataFrame = load_enrolled_traceability()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    participation: pd.DataFrame = load_participation()
    points_table: pd.DataFrame = build_points_table(
        participation=participation, traceability=traceability, grades=grades, enrollment_cross=enrollment_cross)
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

    for subject in const.SUBJECT_OPTIONS:
        scatter[subject] = build_scatter_table(source=pooled_grouped, subject=subject)
        trend[subject] = build_xy_table(source=trend_table, subject=subject)
        cards[subject] = build_card(correlations=correlations, subject=subject)

        if subject != const.SUBJECT_ALL:
            risks[subject] = build_risk_table(
                grouped_points=grouped_points, participation_index=participation_index, cutoff=cutoff, subject=subject)

    all_risks: pd.DataFrame = pd.concat(list(risks.values()), ignore_index=True)
    risks[const.SUBJECT_ALL] = all_risks

    for subject_name in list(risks.keys()):
        risks[subject_name] = sort_by_id_asc(risks[subject_name], const.STUDENT_TABLE_COLUMN)

    result: Dict[str, Dict[str, object]] = {
        const.SCATTER_KEY: scatter,
        const.TREND_KEY: trend,
        const.CARD_KEY: cards,
        const.RISK_TABLE_COLUMN: risks,
    }

    return result
