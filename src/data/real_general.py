from typing import Dict, List

import pandas as pd
import streamlit as st

from data.real_common import (
    load_enrolled_traceability,
    load_enrollment_cross,
    load_grades,
    load_participation,
)
from kpis.kpis_calificaciones import distribucion_de_notas, promedio_general_por_asignatura
from kpis.kpis_participacion import estudiantes_activos_vs_inactivos, sesiones_promedio_por_estudiante
from kpis.kpis_trazabilidad import frecuencia_ingreso
from constants import (
    ACTIVE_COUNT_COLUMN,
    ACTIVE_LABEL,
    ACTIVE_PERCENT_COLUMN,
    ACTIVE_PERCENT_DETAIL_TEMPLATE,
    AVERAGE_ACTIVE_COLUMN,
    AVERAGE_PERCENT_COLUMN,
    CACHE_TTL_SECONDS,
    CARD_AVERAGE_GRADE_TITLE,
    CARD_AVERAGE_SESSIONS_TITLE,
    CARD_ENROLLED_DETAIL,
    CARD_GRADE_SCALE_DETAIL,
    CARD_PER_ACTIVE_STUDENT_DETAIL,
    CONTEXT_ENROLLED_PARTICIPATION_KEY,
    CONTEXT_ENROLLMENT_CROSS_KEY,
    CONTEXT_GRADES_TABLE_KEY,
    CONTEXT_KEY,
    CONTEXT_SESSIONS_TABLE_KEY,
    COUNT_COLUMN,
    DETAIL_KEY,
    DISTRIBUTION_BIN_WIDTH,
    DISTRIBUTION_FROM_COLUMN,
    DISTRIBUTION_KEY,
    DISTRIBUTION_TO_COLUMN,
    ENROLLED_COLUMN,
    ENROLLED_COUNT_COLUMN,
    ENROLLED_LABEL,
    ENTRIES_PER_ACTIVE_USER_COLUMN,
    INACTIVE_COUNT_COLUMN,
    INACTIVE_LABEL,
    INACTIVE_PERCENT_COLUMN,
    INTEGER_FORMAT,
    ONE_DECIMAL_FORMAT,
    PERIOD_COLUMN,
    RANGE_COLUMN,
    RANGE_LABEL_TEMPLATE,
    SCALE_DIVISOR,
    SESSIONS_COLUMN,
    SPINNER_BUILD_ACTIVE_INACTIVE,
    SPINNER_BUILD_GENERAL,
    STATUS_COLUMN,
    STUDENTS_COLUMN,
    SUBJECTS,
    SUBJECT_COLUMN,
    SUBJECT_KEYS,
    TITLE_KEY,
    TREND_KEY,
    USER_COLUMN,
    VALUE_KEY,
    WEEKLY_FREQUENCY,
    WEEK_COLUMN,
    WEEK_LABEL_TEMPLATE,
    WEEK_PREFIX,
)

def select_row(table: pd.DataFrame, subject: str) -> pd.Series:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = table[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = table.loc[is_subject]
    row: pd.Series = selected.iloc[0]

    return row

def keep_enrolled_participation(participation: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.DataFrame:
    pair_columns: list = [SUBJECT_COLUMN, USER_COLUMN]
    is_enrolled: pd.Series = enrollment_cross[ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    enrolled_pairs: pd.DataFrame = enrolled_rows[pair_columns]
    result: pd.DataFrame = participation.merge(enrolled_pairs, on=pair_columns, how="inner")

    return result

def build_cards(subject: str, active_table: pd.DataFrame, grades_table: pd.DataFrame, sessions_table: pd.DataFrame) -> List[Dict[str, str]]:
    active_row: pd.Series = select_row(table=active_table, subject=subject)
    grades_row: pd.Series = select_row(table=grades_table, subject=subject)
    sessions_row: pd.Series = select_row(table=sessions_table, subject=subject)
    enrolled_text: str = str(int(sessions_row[ENROLLED_COUNT_COLUMN]))
    active_text: str = str(int(active_row[ACTIVE_COUNT_COLUMN]))
    inactive_text: str = str(int(active_row[INACTIVE_COUNT_COLUMN]))
    active_percent: str = format(float(active_row[ACTIVE_PERCENT_COLUMN]), INTEGER_FORMAT)
    inactive_percent: str = format(float(active_row[INACTIVE_PERCENT_COLUMN]), INTEGER_FORMAT)
    grade_value: float = float(grades_row[AVERAGE_PERCENT_COLUMN]) / SCALE_DIVISOR
    grade_text: str = format(grade_value, ONE_DECIMAL_FORMAT)
    sessions_text: str = format(float(sessions_row[AVERAGE_ACTIVE_COLUMN]), ONE_DECIMAL_FORMAT)
    active_detail: str = ACTIVE_PERCENT_DETAIL_TEMPLATE.format(percent=active_percent)
    inactive_detail: str = ACTIVE_PERCENT_DETAIL_TEMPLATE.format(percent=inactive_percent)
    cards: List[Dict[str, str]] = [
        {TITLE_KEY: ENROLLED_LABEL, VALUE_KEY: enrolled_text, DETAIL_KEY: CARD_ENROLLED_DETAIL},
        {TITLE_KEY: ACTIVE_LABEL, VALUE_KEY: active_text, DETAIL_KEY: active_detail},
        {TITLE_KEY: INACTIVE_LABEL, VALUE_KEY: inactive_text, DETAIL_KEY: inactive_detail},
        {TITLE_KEY: CARD_AVERAGE_GRADE_TITLE, VALUE_KEY: grade_text, DETAIL_KEY: CARD_GRADE_SCALE_DETAIL},
        {TITLE_KEY: CARD_AVERAGE_SESSIONS_TITLE, VALUE_KEY: sessions_text, DETAIL_KEY: CARD_PER_ACTIVE_STUDENT_DETAIL},
    ]

    return cards

def build_active_inactive(active_table: pd.DataFrame, subject: str) -> pd.DataFrame:
    active_row: pd.Series = select_row(table=active_table, subject=subject)
    active_count: int = int(active_row[ACTIVE_COUNT_COLUMN])
    inactive_count: int = int(active_row[INACTIVE_COUNT_COLUMN])
    table_data: Dict[str, list] = {
        STATUS_COLUMN: [ACTIVE_LABEL, INACTIVE_LABEL],
        COUNT_COLUMN: [active_count, inactive_count],
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_range_label(row_from: int, row_to: int) -> str:
    label_from: int = row_from // SCALE_DIVISOR
    label_to: int = row_to // SCALE_DIVISOR
    label: str = RANGE_LABEL_TEMPLATE.format(start=label_from, end=label_to)

    return label

def build_grade_distribution(distribution: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = distribution[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = distribution.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(DISTRIBUTION_FROM_COLUMN)
    labels: List[str] = []

    for row in sorted_rows.itertuples(index=False):
        row_from: int = getattr(row, DISTRIBUTION_FROM_COLUMN)
        row_to: int = getattr(row, DISTRIBUTION_TO_COLUMN)
        label: str = build_range_label(row_from=row_from, row_to=row_to)
        labels.append(label)

    counts: List[int] = sorted_rows[STUDENTS_COLUMN].tolist()
    table_data: Dict[str, list] = {
        RANGE_COLUMN: labels,
        COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_participation_trend(weekly: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = weekly[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = weekly.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(PERIOD_COLUMN)
    values: List[float] = sorted_rows[ENTRIES_PER_ACTIVE_USER_COLUMN].tolist()
    weeks: List[str] = []
    week_number: int = 1

    for _ in values:
        week_label: str = WEEK_LABEL_TEMPLATE.format(prefix=WEEK_PREFIX, number=week_number)
        weeks.append(week_label)
        week_number = week_number + 1

    table_data: Dict[str, list] = {
        WEEK_COLUMN: weeks,
        SESSIONS_COLUMN: values,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_BUILD_GENERAL)
def build_all() -> Dict[str, Dict[str, object]]:
    participation: pd.DataFrame = load_participation()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    traceability: pd.DataFrame = load_enrolled_traceability()
    enrolled_participation: pd.DataFrame = keep_enrolled_participation(participation=participation, enrollment_cross=enrollment_cross)
    grades_table: pd.DataFrame = promedio_general_por_asignatura(calificaciones=grades, cruce=enrollment_cross, matriculados=True)
    sessions_table: pd.DataFrame = sesiones_promedio_por_estudiante(trazabilidad=traceability, cruce=enrollment_cross)
    distribution: pd.DataFrame = distribucion_de_notas(calificaciones=grades, cruce=enrollment_cross, ancho_bin=DISTRIBUTION_BIN_WIDTH, matriculados=True)
    weekly: pd.DataFrame = frecuencia_ingreso(df=traceability, freq=WEEKLY_FREQUENCY)
    distributions: Dict[str, pd.DataFrame] = {}
    trends: Dict[str, pd.DataFrame] = {}

    for subject in SUBJECTS:
        distributions[subject] = build_grade_distribution(distribution=distribution, subject=subject)
        trends[subject] = build_participation_trend(weekly=weekly, subject=subject)

    result: Dict[str, Dict[str, object]] = {
        DISTRIBUTION_KEY: distributions,
        TREND_KEY: trends,
        CONTEXT_KEY: {
            CONTEXT_ENROLLED_PARTICIPATION_KEY: enrolled_participation,
            CONTEXT_ENROLLMENT_CROSS_KEY: enrollment_cross,
            CONTEXT_GRADES_TABLE_KEY: grades_table,
            CONTEXT_SESSIONS_TABLE_KEY: sessions_table,
        },
    }

    return result

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_BUILD_ACTIVE_INACTIVE)
def active_table_for_days(days: int) -> pd.DataFrame:
    context: Dict[str, object] = build_all()[CONTEXT_KEY]
    enrolled_participation: pd.DataFrame = context[CONTEXT_ENROLLED_PARTICIPATION_KEY]
    enrollment_cross: pd.DataFrame = context[CONTEXT_ENROLLMENT_CROSS_KEY]
    result: pd.DataFrame = estudiantes_activos_vs_inactivos(participacion=enrolled_participation, cruce=enrollment_cross, dias=days)

    return result

def general_cards_for_days(subject: str, days: int) -> List[Dict[str, str]]:
    active_table: pd.DataFrame = active_table_for_days(days)
    context: Dict[str, object] = build_all()[CONTEXT_KEY]
    grades_table: pd.DataFrame = context[CONTEXT_GRADES_TABLE_KEY]
    sessions_table: pd.DataFrame = context[CONTEXT_SESSIONS_TABLE_KEY]
    result: List[Dict[str, str]] = build_cards(subject=subject, active_table=active_table, grades_table=grades_table, sessions_table=sessions_table)

    return result

def active_inactive_for_days(subject: str, days: int) -> pd.DataFrame:
    active_table: pd.DataFrame = active_table_for_days(days)
    result: pd.DataFrame = build_active_inactive(active_table=active_table, subject=subject)

    return result
