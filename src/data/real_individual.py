from typing import Any, Dict, List, Optional, Tuple
from data.real_common import (load_enrolled_traceability, load_enrollment_cross, load_grades, load_participation, sum_tables)
from kpis.kpis_calificaciones import condicion_por_estudiante, nota_por_estudiante
from kpis.kpis_trazabilidad import TIPOS, clasificar_interacciones, frecuencia_ingreso
import pandas as pd
import streamlit as st
import constants as const

def build_names(participation: pd.DataFrame) -> Dict[Tuple[str, str], str]:
    names: Dict[Tuple[str, str], str] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        last_name: str = getattr(row, const.LAST_NAME_COLUMN)
        first_name: str = getattr(row, const.FIRST_NAME_COLUMN)
        full_name: str = const.FULL_NAME_TEMPLATE.format(last_name=last_name, first_name=first_name)
        pair: Tuple[str, str] = (subject_key, user)
        names[pair] = full_name

    return names

def group_by_pair(table: pd.DataFrame) -> Dict[Tuple[str, str], pd.DataFrame]:
    groups: Dict[Tuple[str, str], pd.DataFrame] = {}
    grouped: pd.core.groupby.DataFrameGroupBy = table.groupby([const.SUBJECT_COLUMN, const.USER_COLUMN])

    for key, group in grouped:
        subject_key: str = key[0]
        user: str = key[1]
        pair: Tuple[str, str] = (subject_key, user)
        groups[pair] = group

    return groups

def build_grades_table(student_grades: Optional[pd.DataFrame]) -> pd.DataFrame:
    instruments: List[str] = []
    values: List[float] = []

    if student_grades is not None:
        has_maximum: pd.Series = student_grades[const.MAXIMUM_COLUMN] > 0
        valid: pd.DataFrame = student_grades.loc[has_maximum]
        ordered: pd.DataFrame = valid.sort_values(const.FILE_ID_COLUMN)

        for row in ordered.itertuples(index=False):
            instrument: str = getattr(row, const.INSTRUMENT_SOURCE_COLUMN)
            obtained: float = float(getattr(row, const.OBTAINED_COLUMN))
            maximum: float = float(getattr(row, const.MAXIMUM_COLUMN))
            ratio: float = obtained / maximum
            scaled: float = ratio * const.SCALE_DIVISOR
            rounded: float = round(scaled, const.INDIVIDUAL_GRADE_DECIMALS)
            instruments.append(instrument)
            values.append(rounded)

    table_data: Dict[str, list] = {
        const.INSTRUMENT_COLUMN: instruments,
        const.GRADE_COLUMN: values,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_participation_table(student_traceability: Optional[pd.DataFrame], periods: List[str]) -> pd.DataFrame:
    entries_by_period: Dict[str, int] = {}

    if student_traceability is not None:
        weekly: pd.DataFrame = frecuencia_ingreso(df=student_traceability, freq=const.WEEKLY_FREQUENCY)

        for row in weekly.itertuples(index=False):
            period: str = getattr(row, const.PERIOD_COLUMN)
            entries: int = int(getattr(row, const.ENTRIES_COLUMN))
            entries_by_period[period] = entries

    weeks: List[str] = []
    sessions: List[int] = []
    week_number: int = 1

    for period_label in periods:
        week_label: str = const.WEEK_LABEL_TEMPLATE.format(prefix=const.WEEK_PREFIX, number=week_number)
        period_entries: int = entries_by_period.get(period_label, 0)
        weeks.append(week_label)
        sessions.append(period_entries)
        week_number = week_number + 1

    table_data: Dict[str, list] = {
        const.WEEK_COLUMN: weeks,
        const.SESSIONS_COLUMN: sessions,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_traceability_table(student_traceability: Optional[pd.DataFrame]) -> pd.DataFrame:
    counts: Dict[str, int] = {}

    for type_name in TIPOS:
        counts[type_name] = 0

    if student_traceability is not None:
        types: pd.Series = clasificar_interacciones(df=student_traceability)
        type_counts: pd.Series = types.value_counts()

        for type_name, type_value in type_counts.items():
            counts[type_name] = int(type_value)

    actions: List[str] = list(counts.keys())
    values: List[int] = list(counts.values())
    table_data: Dict[str, list] = {
        const.ACTION_COLUMN: actions,
        const.COUNT_COLUMN: values,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_percents(grades: pd.DataFrame) -> Dict[Tuple[str, str], float]:
    student_grades: pd.DataFrame = nota_por_estudiante(calificaciones=grades)
    percents: Dict[Tuple[str, str], float] = {}

    for row in student_grades.itertuples(index=False):
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        percents[pair] = float(getattr(row, const.GRADE_PERCENT_COLUMN))

    return percents

def build_traffic_light(condition: Optional[str], percent: Optional[float] = None) -> Tuple[str, str]:
    color: str
    text: str

    if condition is None:
        color = const.TRAFFIC_RED
        text = const.NOT_PRESENTED_LABEL
    else:
        color = const.CONDITION_TRAFFIC_COLORS[condition]
        text = const.CONDITION_LABELS[condition]

    if percent is not None:
        text = const.TRAFFIC_LIGHT_PERCENT_TEMPLATE.format(text=text, percent=round(percent))

    result: Tuple[str, str] = (color, text)

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
        conditions[pair] = condition

    return conditions

def build_periods(traceability: pd.DataFrame, subject_key: str) -> List[str]:
    is_subject: pd.Series = traceability[const.SUBJECT_COLUMN] == subject_key
    subject_rows: pd.DataFrame = traceability.loc[is_subject]
    weekly: pd.DataFrame = frecuencia_ingreso(df=subject_rows, freq=const.WEEKLY_FREQUENCY)
    periods: List[str] = weekly[const.PERIOD_COLUMN].tolist()
    sorted_periods: List[str] = sorted(periods)

    return sorted_periods

def build_all_subjects_entry(entries: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    grade_tables: List[pd.DataFrame] = []
    participation_series: Dict[str, pd.DataFrame] = {}
    traceability_tables: List[pd.DataFrame] = []
    lights: List[Tuple[Optional[str], str, str]] = []
    no_grades: List[str] = []
    not_enrolled: List[str] = []

    for subject in const.SUBJECTS:
        if subject not in entries:
            not_enrolled.append(subject)
            lights.append((subject, const.TRAFFIC_GRAY, const.NOT_ENROLLED_LABEL))
            continue

        entry: Dict[str, Any] = entries[subject]
        grade_tables.append(entry[const.GRADES_KEY].assign(**{const.SUBJECT_NAME_COLUMN: subject}))
        participation_series[subject] = entry[const.PARTICIPATION_KEY]
        traceability_tables.append(entry[const.TRACEABILITY_KEY])
        light: Tuple[Optional[str], str, str] = entry[const.TRAFFIC_LIGHTS_KEY][0]
        light_color: str = light[1]
        light_text: str = light[2]
        lights.append((subject, light_color, light_text))

        if len(entry[const.GRADES_KEY]) == 0:
            no_grades.append(subject)

    grades_all: pd.DataFrame = pd.concat(grade_tables, ignore_index=True)
    traceability_all: pd.DataFrame = sum_tables(traceability_tables, [const.ACTION_COLUMN], [const.COUNT_COLUMN])
    result: Dict[str, Any] = {
        const.GRADES_KEY: grades_all,
        const.PARTICIPATION_SERIES_KEY: participation_series,
        const.TRACEABILITY_KEY: traceability_all,
        const.TRAFFIC_LIGHTS_KEY: lights,
        const.NO_GRADES_KEY: no_grades,
        const.NOT_ENROLLED_KEY: not_enrolled,
    }

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_INDIVIDUAL)
def build_all() -> Tuple[List[str], Dict[str, Dict[str, Dict[str, Any]]], Dict[str, List[str]]]:
    participation: pd.DataFrame = load_participation()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    traceability: pd.DataFrame = load_enrolled_traceability()
    names: Dict[Tuple[str, str], str] = build_names(participation=participation)
    grade_groups: Dict[Tuple[str, str], pd.DataFrame] = group_by_pair(table=grades)
    traceability_groups: Dict[Tuple[str, str], pd.DataFrame] = group_by_pair(table=traceability)
    conditions: Dict[Tuple[str, str], str] = build_conditions(grades=grades, enrollment_cross=enrollment_cross)
    percents: Dict[Tuple[str, str], float] = build_percents(grades=grades)
    is_enrolled: pd.Series = enrollment_cross[const.ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    labels_by_user: Dict[str, str] = {}
    subject_entries: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for subject in const.SUBJECTS:
        subject_key: str = const.SUBJECT_KEYS[subject]
        periods: List[str] = build_periods(traceability=traceability, subject_key=subject_key)
        is_subject: pd.Series = enrolled_rows[const.SUBJECT_COLUMN] == subject_key
        subject_rows: pd.DataFrame = enrolled_rows.loc[is_subject]
        users: List[str] = sorted(subject_rows[const.USER_COLUMN].tolist())

        for user in users:
            pair: Tuple[str, str] = (subject_key, user)
            full_name: str = names[pair]
            labels_by_user.setdefault(user, const.STUDENT_LABEL_TEMPLATE.format(user=user, full_name=full_name))
            grades_table: pd.DataFrame = build_grades_table(student_grades=grade_groups.get(pair))
            participation_table: pd.DataFrame = build_participation_table(
                student_traceability=traceability_groups.get(pair), periods=periods)
            traceability_table: pd.DataFrame = build_traceability_table(
                student_traceability=traceability_groups.get(pair))
            color: str
            text: str
            color, text = build_traffic_light(condition=conditions.get(pair), percent=percents.get(pair))
            entry: Dict[str, Any] = {
                const.GRADES_KEY: grades_table,
                const.PARTICIPATION_KEY: participation_table,
                const.TRACEABILITY_KEY: traceability_table,
                const.TRAFFIC_LIGHTS_KEY: [(None, color, text)],
            }
            subject_entries.setdefault(user, {})[subject] = entry

    student_data: Dict[str, Dict[str, Dict[str, Any]]] = {}
    student_subjects: Dict[str, List[str]] = {}

    for user in sorted(labels_by_user.keys()):
        label: str = labels_by_user[user]
        entries: Dict[str, Dict[str, Any]] = subject_entries[user]
        student_data[label] = dict(entries)
        student_data[label][const.SUBJECT_ALL] = build_all_subjects_entry(entries=entries)
        student_subjects[label] = list(entries.keys())

    options: List[str] = list(student_data.keys())
    result: Tuple[List[str], Dict[str, Dict[str, Dict[str, Any]]], Dict[str, List[str]]] = (options, student_data, student_subjects)

    return result
