from typing import Dict, List
from data.services.real_common import load_enrolled_traceability, load_enrollment_cross, load_grades, load_participation
from data.kpis.kpis_calificaciones import distribucion_de_notas, promedio_general_por_asignatura
from data.kpis.kpis_participacion import estudiantes_activos_vs_inactivos, sesiones_promedio_por_estudiante
from data.kpis.kpis_trazabilidad import frecuencia_ingreso
import pandas as pd
import streamlit as st
import constants as const

def select_row(table: pd.DataFrame, subject: str) -> pd.Series:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = table[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = table.loc[is_subject]
    row: pd.Series = selected.iloc[0]

    return row

def keep_enrolled_participation(participation: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.DataFrame:
    pair_columns: list = [const.SUBJECT_COLUMN, const.USER_COLUMN]
    is_enrolled: pd.Series = enrollment_cross[const.ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    enrolled_pairs: pd.DataFrame = enrolled_rows[pair_columns]
    result: pd.DataFrame = participation.merge(enrolled_pairs, on=pair_columns, how="inner")

    return result

def build_cards(subject: str, active_table: pd.DataFrame, grades_table: pd.DataFrame, sessions_table: pd.DataFrame) -> List[Dict[str, str]]:
    active_row: pd.Series = select_row(table=active_table, subject=subject)
    grades_row: pd.Series = select_row(table=grades_table, subject=subject)
    sessions_row: pd.Series = select_row(table=sessions_table, subject=subject)
    enrolled_text: str = str(int(sessions_row[const.ENROLLED_COUNT_COLUMN]))
    active_text: str = str(int(active_row[const.ACTIVE_COUNT_COLUMN]))
    inactive_text: str = str(int(active_row[const.INACTIVE_COUNT_COLUMN]))
    active_percent: str = format(float(active_row[const.ACTIVE_PERCENT_COLUMN]), const.INTEGER_FORMAT)
    inactive_percent: str = format(float(active_row[const.INACTIVE_PERCENT_COLUMN]), const.INTEGER_FORMAT)
    grade_value: float = float(grades_row[const.AVERAGE_PERCENT_COLUMN]) / const.SCALE_DIVISOR
    grade_text: str = format(grade_value, const.ONE_DECIMAL_FORMAT)
    sessions_text: str = format(float(sessions_row[const.AVERAGE_ACTIVE_COLUMN]), const.ONE_DECIMAL_FORMAT)
    active_detail: str = const.ACTIVE_PERCENT_DETAIL_TEMPLATE.format(percent=active_percent)
    inactive_detail: str = const.ACTIVE_PERCENT_DETAIL_TEMPLATE.format(percent=inactive_percent)
    cards: List[Dict[str, str]] = [
        {const.TITLE_KEY: const.ENROLLED_LABEL, const.VALUE_KEY: enrolled_text, const.DETAIL_KEY: const.CARD_ENROLLED_DETAIL},
        {const.TITLE_KEY: const.ACTIVE_LABEL, const.VALUE_KEY: active_text, const.DETAIL_KEY: active_detail},
        {const.TITLE_KEY: const.INACTIVE_LABEL, const.VALUE_KEY: inactive_text, const.DETAIL_KEY: inactive_detail},
        {const.TITLE_KEY: const.CARD_AVERAGE_GRADE_TITLE, const.VALUE_KEY: grade_text, const.DETAIL_KEY: const.CARD_GRADE_SCALE_DETAIL},
        {const.TITLE_KEY: const.CARD_AVERAGE_SESSIONS_TITLE, const.VALUE_KEY: sessions_text, const.DETAIL_KEY: const.CARD_PER_ACTIVE_STUDENT_DETAIL},
    ]

    return cards

def build_active_inactive(active_table: pd.DataFrame, subject: str) -> pd.DataFrame:
    active_row: pd.Series = select_row(table=active_table, subject=subject)
    active_count: int = int(active_row[const.ACTIVE_COUNT_COLUMN])
    inactive_count: int = int(active_row[const.INACTIVE_COUNT_COLUMN])
    table_data: Dict[str, list] = {
        const.STATUS_COLUMN: [const.ACTIVE_LABEL, const.INACTIVE_LABEL],
        const.COUNT_COLUMN: [active_count, inactive_count],
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_range_label(row_from: int, row_to: int) -> str:
    label_from: int = row_from // const.SCALE_DIVISOR
    label_to: int = row_to // const.SCALE_DIVISOR
    label: str = const.RANGE_LABEL_TEMPLATE.format(start=label_from, end=label_to)

    return label

def build_grade_distribution(distribution: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = distribution[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = distribution.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(const.DISTRIBUTION_FROM_COLUMN)
    labels: List[str] = []

    for row in sorted_rows.itertuples(index=False):
        row_from: int = getattr(row, const.DISTRIBUTION_FROM_COLUMN)
        row_to: int = getattr(row, const.DISTRIBUTION_TO_COLUMN)
        label: str = build_range_label(row_from=row_from, row_to=row_to)
        labels.append(label)

    counts: List[int] = sorted_rows[const.STUDENTS_COLUMN].tolist()
    table_data: Dict[str, list] = {
        const.RANGE_COLUMN: labels,
        const.COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_participation_trend(weekly: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = weekly[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = weekly.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(const.PERIOD_COLUMN)
    values: List[float] = sorted_rows[const.ENTRIES_PER_ACTIVE_USER_COLUMN].tolist()
    weeks: List[str] = []
    week_number: int = 1

    for _ in values:
        week_label: str = const.WEEK_LABEL_TEMPLATE.format(prefix=const.WEEK_PREFIX, number=week_number)
        weeks.append(week_label)
        week_number = week_number + 1

    table_data: Dict[str, list] = {
        const.WEEK_COLUMN: weeks,
        const.SESSIONS_COLUMN: values,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_GENERAL)
def build_all() -> Dict[str, Dict[str, object]]:
    participation: pd.DataFrame = load_participation()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    traceability: pd.DataFrame = load_enrolled_traceability()
    enrolled_participation: pd.DataFrame = keep_enrolled_participation(
        participation=participation, enrollment_cross=enrollment_cross)
    grades_table: pd.DataFrame = promedio_general_por_asignatura(
        calificaciones=grades, cruce=enrollment_cross, matriculados=True)
    sessions_table: pd.DataFrame = sesiones_promedio_por_estudiante(trazabilidad=traceability, cruce=enrollment_cross)
    distribution: pd.DataFrame = distribucion_de_notas(
        calificaciones=grades, cruce=enrollment_cross, ancho_bin=const.DISTRIBUTION_BIN_WIDTH, matriculados=True)
    weekly: pd.DataFrame = frecuencia_ingreso(df=traceability, freq=const.WEEKLY_FREQUENCY)
    distributions: Dict[str, pd.DataFrame] = {}
    trends: Dict[str, pd.DataFrame] = {}

    for subject in const.SUBJECTS:
        distributions[subject] = build_grade_distribution(distribution=distribution, subject=subject)
        trends[subject] = build_participation_trend(weekly=weekly, subject=subject)

    result: Dict[str, Dict[str, object]] = {
        const.DISTRIBUTION_KEY: distributions,
        const.TREND_KEY: trends,
        const.CONTEXT_KEY: {
            const.CONTEXT_ENROLLED_PARTICIPATION_KEY: enrolled_participation,
            const.CONTEXT_ENROLLMENT_CROSS_KEY: enrollment_cross,
            const.CONTEXT_GRADES_TABLE_KEY: grades_table,
            const.CONTEXT_SESSIONS_TABLE_KEY: sessions_table,
        },
    }

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_ACTIVE_INACTIVE)
def active_table_for_days(days: int) -> pd.DataFrame:
    context: Dict[str, object] = build_all()[const.CONTEXT_KEY]
    enrolled_participation: pd.DataFrame = context[const.CONTEXT_ENROLLED_PARTICIPATION_KEY]
    enrollment_cross: pd.DataFrame = context[const.CONTEXT_ENROLLMENT_CROSS_KEY]
    result: pd.DataFrame = estudiantes_activos_vs_inactivos(
        participacion=enrolled_participation, cruce=enrollment_cross, dias=days)

    return result

def general_cards_for_days(subject: str, days: int) -> List[Dict[str, str]]:
    active_table: pd.DataFrame = active_table_for_days(days)
    context: Dict[str, object] = build_all()[const.CONTEXT_KEY]
    grades_table: pd.DataFrame = context[const.CONTEXT_GRADES_TABLE_KEY]
    sessions_table: pd.DataFrame = context[const.CONTEXT_SESSIONS_TABLE_KEY]
    result: List[Dict[str, str]] = build_cards(
        subject=subject, active_table=active_table, grades_table=grades_table, sessions_table=sessions_table)

    return result

def active_inactive_for_days(subject: str, days: int) -> pd.DataFrame:
    active_table: pd.DataFrame = active_table_for_days(days)
    result: pd.DataFrame = build_active_inactive(active_table=active_table, subject=subject)

    return result
