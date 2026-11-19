from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

from data.real_common import (
    load_enrolled_traceability,
    load_enrollment_cross,
    load_participation,
    window_start,
)
from kpis.kpis_trazabilidad import interacciones_diarias
from constants import (
    ACCESSES_COLUMN,
    ACTIVITIES_COLUMN,
    ACTIVITY_KEY,
    ANCHOR_DATE,
    CACHE_TTL_SECONDS,
    CATALOG_KEY,
    DAILY_FREQUENCY,
    DATE_COLUMN,
    DATE_FORMAT,
    DATE_RANGES,
    DAY_COLUMN,
    ENROLLED_COLUMN,
    ENTRY_COLUMN,
    FIRST_NAME_COLUMN,
    FULL_NAME_TEMPLATE,
    INTERACTIONS_COLUMN,
    LAST_NAME_COLUMN,
    SPINNER_BUILD_PARTICIPATION,
    SPINNER_BUILD_STUDENT_ACTIVITY,
    STUDENT_ALL,
    STUDENT_LABEL_TEMPLATE,
    SUBJECTS,
    SUBJECT_ALL,
    SUBJECT_COLUMN,
    SUBJECT_KEYS,
    USER_COLUMN,
)

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

def build_names(participation: pd.DataFrame) -> Dict[Tuple[str, str], str]:
    names: Dict[Tuple[str, str], str] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        last_name: str = getattr(row, LAST_NAME_COLUMN)
        first_name: str = getattr(row, FIRST_NAME_COLUMN)
        full_name: str = FULL_NAME_TEMPLATE.format(last_name=last_name, first_name=first_name)
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
            label: str = STUDENT_LABEL_TEMPLATE.format(user=user, full_name=full_name)
            labels_to_users[label] = user

        catalog[subject] = labels_to_users

    return catalog

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_BUILD_PARTICIPATION)
def build_all() -> Dict[str, Dict[str, object]]:
    daily: pd.DataFrame = build_daily_table()
    activity: Dict[str, Dict[str, pd.DataFrame]] = build_by_range(
        daily=daily,
        source_column=INTERACTIONS_COLUMN,
        output_column=ACTIVITIES_COLUMN,
    )
    accesses: Dict[str, Dict[str, pd.DataFrame]] = build_by_range(
        daily=daily,
        source_column=ACCESSES_COLUMN,
        output_column=ACCESSES_COLUMN,
    )
    catalog: Dict[str, Dict[str, str]] = build_student_catalog()
    result: Dict[str, Dict[str, object]] = {
        ACTIVITY_KEY: activity,
        ACCESSES_COLUMN: accesses,
        CATALOG_KEY: catalog,
    }

    return result

def get_subject_options() -> List[str]:
    options: List[str] = [SUBJECT_ALL]
    options.extend(SUBJECTS)

    return options

def sum_subjects(tables_by_subject: Dict[str, pd.DataFrame], value_column: str) -> pd.DataFrame:
    tables: List[pd.DataFrame] = list(tables_by_subject.values())
    combined: pd.DataFrame = pd.concat(tables, ignore_index=True)
    grouped: pd.Series = combined.groupby(DATE_COLUMN)[value_column].sum()
    sorted_values: pd.Series = grouped.sort_index()
    result: pd.DataFrame = sorted_values.reset_index()

    return result

def get_student_options(subject: str) -> List[str]:
    if subject == SUBJECT_ALL:
        return [STUDENT_ALL]

    catalog: Dict[str, Dict[str, str]] = build_all()[CATALOG_KEY]
    labels_to_users: Dict[str, str] = catalog[subject]
    labels: List[str] = list(labels_to_users.keys())
    options: List[str] = [STUDENT_ALL]
    options.extend(labels)

    return options

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_BUILD_STUDENT_ACTIVITY)
def build_student_daily(subject: str, student: str, range_label: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    catalog: Dict[str, Dict[str, str]] = build_all()[CATALOG_KEY]
    labels_to_users: Dict[str, str] = catalog[subject]
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
        activity_by_date: Dict[str, Dict[str, pd.DataFrame]] = build_all()[ACTIVITY_KEY]
        activity_of_range: Dict[str, pd.DataFrame] = activity_by_date[date_range]
        if subject == SUBJECT_ALL:
            result = sum_subjects(activity_of_range, ACTIVITIES_COLUMN)
        else:
            result = activity_of_range[subject]
    else:
        daily: pd.DataFrame = build_student_daily(subject=subject, student=student, range_label=date_range)
        columns: List[str] = [DATE_COLUMN, ACTIVITIES_COLUMN]
        result = daily[columns]

    return result

def get_accesses(subject: str, date_range: str, student: str) -> pd.DataFrame:
    result: pd.DataFrame

    if student == STUDENT_ALL:
        access_evolution: Dict[str, Dict[str, pd.DataFrame]] = build_all()[ACCESSES_COLUMN]
        accesses_of_range: Dict[str, pd.DataFrame] = access_evolution[date_range]
        if subject == SUBJECT_ALL:
            result = sum_subjects(accesses_of_range, ACCESSES_COLUMN)
        else:
            result = accesses_of_range[subject]
    else:
        daily: pd.DataFrame = build_student_daily(subject=subject, student=student, range_label=date_range)
        columns: List[str] = [DATE_COLUMN, ACCESSES_COLUMN]
        result = daily[columns]

    return result
