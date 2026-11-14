from typing import Dict, List, Tuple

import pandas as pd

from data.real_common import (
    ANCHOR_DATE,
    DATE_RANGES,
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrolled_traceability,
    load_enrollment_cross,
    load_participation,
    window_start,
)
from kpis.kpis_trazabilidad import interacciones_diarias

SUBJECT_COLUMN: str = "materia"
DAY_COLUMN: str = "dia"
INTERACTIONS_COLUMN: str = "interacciones"
ENTRY_COLUMN: str = "es_ingreso"
ACCESSES_COLUMN: str = "accesses"
ACTIVITIES_COLUMN: str = "activities"
DATE_COLUMN: str = "date"
DATE_FORMAT: str = "%Y-%m-%d"
USER_COLUMN: str = "usuario"
ENROLLED_COLUMN: str = "matriculado"
LAST_NAME_COLUMN: str = "apellido"
FIRST_NAME_COLUMN: str = "nombre"
DAILY_FREQUENCY: str = "D"
STUDENT_ALL: str = "Todos los estudiantes"

def build_daily_accesses(traceability: pd.DataFrame) -> pd.DataFrame:
    is_entry: pd.Series = traceability[ENTRY_COLUMN]
    entries: pd.DataFrame = traceability.loc[is_entry]
    group_columns: list = [SUBJECT_COLUMN, DAY_COLUMN]
    grouped: pd.core.groupby.DataFrameGroupBy = entries.groupby(group_columns)
    counts: pd.Series = grouped.size()
    named_counts: pd.Series = counts.rename(ACCESSES_COLUMN)
    result: pd.DataFrame = named_counts.reset_index()

    return result

def build_daily_table() -> pd.DataFrame:
    traceability: pd.DataFrame = load_enrolled_traceability()
    daily: pd.DataFrame = interacciones_diarias(df=traceability)
    daily_columns: list = [SUBJECT_COLUMN, DAY_COLUMN, INTERACTIONS_COLUMN]
    daily_selected: pd.DataFrame = daily[daily_columns]
    accesses: pd.DataFrame = build_daily_accesses(traceability=traceability)
    join_columns: list = [SUBJECT_COLUMN, DAY_COLUMN]
    merged: pd.DataFrame = daily_selected.merge(accesses, on=join_columns, how="left")
    filled: pd.Series = merged[ACCESSES_COLUMN].fillna(0)
    merged[ACCESSES_COLUMN] = filled.astype(int)

    return merged

def build_range_table(daily: pd.DataFrame, subject: str, range_label: str, source_column: str, output_column: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    start: pd.Timestamp = window_start(range_label=range_label)
    is_subject: pd.Series = daily[SUBJECT_COLUMN] == subject_key
    is_in_window: pd.Series = daily[DAY_COLUMN] >= start
    mask: pd.Series = is_subject & is_in_window
    selected: pd.DataFrame = daily.loc[mask]
    sorted_rows: pd.DataFrame = selected.sort_values(DAY_COLUMN)
    days: pd.Series = sorted_rows[DAY_COLUMN]
    date_text: pd.Series = days.dt.strftime(DATE_FORMAT)
    values: pd.Series = sorted_rows[source_column]
    table_data: Dict[str, list] = {
        DATE_COLUMN: date_text.tolist(),
        output_column: values.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_by_range(daily: pd.DataFrame, source_column: str, output_column: str) -> Dict[str, Dict[str, pd.DataFrame]]:
    result: Dict[str, Dict[str, pd.DataFrame]] = {}

    for range_label in DATE_RANGES:
        tables_by_subject: Dict[str, pd.DataFrame] = {}

        for subject in SUBJECTS:
            table: pd.DataFrame = build_range_table(
                daily=daily,
                subject=subject,
                range_label=range_label,
                source_column=source_column,
                output_column=output_column,
            )
            tables_by_subject[subject] = table

        result[range_label] = tables_by_subject

    return result

DAILY_TABLE: pd.DataFrame = build_daily_table()

ACTIVITY_BY_DATE: Dict[str, Dict[str, pd.DataFrame]] = build_by_range(
    daily=DAILY_TABLE,
    source_column=INTERACTIONS_COLUMN,
    output_column=ACTIVITIES_COLUMN,
)

ACCESS_EVOLUTION: Dict[str, Dict[str, pd.DataFrame]] = build_by_range(
    daily=DAILY_TABLE,
    source_column=ACCESSES_COLUMN,
    output_column=ACCESSES_COLUMN,
)

def build_names(participation: pd.DataFrame) -> Dict[Tuple[str, str], str]:
    names: Dict[Tuple[str, str], str] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        last_name: str = getattr(row, LAST_NAME_COLUMN)
        first_name: str = getattr(row, FIRST_NAME_COLUMN)
        full_name: str = f"{last_name}, {first_name}"
        pair: Tuple[str, str] = (subject_key, user)
        names[pair] = full_name

    return names

def build_student_catalog() -> Dict[str, Dict[str, str]]:
    participation: pd.DataFrame = load_participation()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    names: Dict[Tuple[str, str], str] = build_names(participation=participation)
    is_enrolled: pd.Series = enrollment_cross[ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    catalog: Dict[str, Dict[str, str]] = {}

    for subject in SUBJECTS:
        subject_key: str = SUBJECT_KEYS[subject]
        is_subject: pd.Series = enrolled_rows[SUBJECT_COLUMN] == subject_key
        subject_rows: pd.DataFrame = enrolled_rows.loc[is_subject]
        users: List[str] = sorted(subject_rows[USER_COLUMN].tolist())
        labels_to_users: Dict[str, str] = {}

        for user in users:
            pair: Tuple[str, str] = (subject_key, user)
            full_name: str = names[pair]
            label: str = f"{user} – {full_name}"
            labels_to_users[label] = user

        catalog[subject] = labels_to_users

    return catalog

STUDENT_CATALOG: Dict[str, Dict[str, str]] = build_student_catalog()

def get_student_options(subject: str) -> List[str]:
    labels_to_users: Dict[str, str] = STUDENT_CATALOG[subject]
    labels: List[str] = list(labels_to_users.keys())
    options: List[str] = [STUDENT_ALL]
    options.extend(labels)

    return options

def build_student_daily(subject: str, student: str, range_label: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    labels_to_users: Dict[str, str] = STUDENT_CATALOG[subject]
    user: str = labels_to_users[student]
    traceability: pd.DataFrame = load_enrolled_traceability()
    is_subject: pd.Series = traceability[SUBJECT_COLUMN] == subject_key
    is_user: pd.Series = traceability[USER_COLUMN] == user
    mask: pd.Series = is_subject & is_user
    rows: pd.DataFrame = traceability.loc[mask]
    start: pd.Timestamp = window_start(range_label=range_label)
    days: pd.DatetimeIndex = pd.date_range(start=start, end=ANCHOR_DATE, freq=DAILY_FREQUENCY)
    interactions_by_day: pd.Series = rows.groupby(DAY_COLUMN).size()
    is_entry: pd.Series = rows[ENTRY_COLUMN]
    entry_rows: pd.DataFrame = rows.loc[is_entry]
    entries_by_day: pd.Series = entry_rows.groupby(DAY_COLUMN).size()
    interactions: pd.Series = interactions_by_day.reindex(days, fill_value=0)
    entries: pd.Series = entries_by_day.reindex(days, fill_value=0)
    date_text: List[str] = days.strftime(DATE_FORMAT).tolist()
    table_data: Dict[str, list] = {
        DATE_COLUMN: date_text,
        ACTIVITIES_COLUMN: interactions.tolist(),
        ACCESSES_COLUMN: entries.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def get_activity(subject: str, date_range: str, student: str) -> pd.DataFrame:
    result: pd.DataFrame

    if student == STUDENT_ALL:
        activity_of_range: Dict[str, pd.DataFrame] = ACTIVITY_BY_DATE[date_range]
        result = activity_of_range[subject]
    else:
        daily: pd.DataFrame = build_student_daily(subject=subject, student=student, range_label=date_range)
        columns: List[str] = [DATE_COLUMN, ACTIVITIES_COLUMN]
        result = daily[columns]

    return result

def get_accesses(subject: str, date_range: str, student: str) -> pd.DataFrame:
    result: pd.DataFrame

    if student == STUDENT_ALL:
        accesses_of_range: Dict[str, pd.DataFrame] = ACCESS_EVOLUTION[date_range]
        result = accesses_of_range[subject]
    else:
        daily: pd.DataFrame = build_student_daily(subject=subject, student=student, range_label=date_range)
        columns: List[str] = [DATE_COLUMN, ACCESSES_COLUMN]
        result = daily[columns]

    return result
