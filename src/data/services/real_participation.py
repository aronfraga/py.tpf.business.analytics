from typing import Dict, List, Tuple
from data.services.real_common import load_enrolled_traceability, load_enrollment_cross, load_participation, window_start
from data.kpis.kpis_trazabilidad import interacciones_diarias
import pandas as pd
import streamlit as st
import constants as const

def build_daily_accesses(traceability: pd.DataFrame) -> pd.DataFrame:
    is_entry: pd.Series = traceability[const.ENTRY_COLUMN]
    entries: pd.DataFrame = traceability.loc[is_entry]
    group_columns: list = [const.SUBJECT_COLUMN, const.DAY_COLUMN]
    grouped: pd.core.groupby.DataFrameGroupBy = entries.groupby(group_columns)
    counts: pd.Series = grouped.size()
    named_counts: pd.Series = counts.rename(const.ACCESSES_COLUMN)
    result: pd.DataFrame = named_counts.reset_index()

    return result

def build_daily_table() -> pd.DataFrame:
    traceability: pd.DataFrame = load_enrolled_traceability()
    daily: pd.DataFrame = interacciones_diarias(df=traceability)
    daily_columns: list = [const.SUBJECT_COLUMN, const.DAY_COLUMN, const.INTERACTIONS_COLUMN]
    daily_selected: pd.DataFrame = daily[daily_columns]
    accesses: pd.DataFrame = build_daily_accesses(traceability=traceability)
    join_columns: list = [const.SUBJECT_COLUMN, const.DAY_COLUMN]
    merged: pd.DataFrame = daily_selected.merge(accesses, on=join_columns, how="left")
    filled: pd.Series = merged[const.ACCESSES_COLUMN].fillna(0)
    merged[const.ACCESSES_COLUMN] = filled.astype(int)

    return merged

def build_range_table(daily: pd.DataFrame, subject: str, range_label: str, source_column: str, output_column: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    start: pd.Timestamp = window_start(range_label=range_label)
    is_subject: pd.Series = daily[const.SUBJECT_COLUMN] == subject_key
    is_in_window: pd.Series = daily[const.DAY_COLUMN] >= start
    mask: pd.Series = is_subject & is_in_window
    selected: pd.DataFrame = daily.loc[mask]
    sorted_rows: pd.DataFrame = selected.sort_values(const.DAY_COLUMN)
    days: pd.Series = sorted_rows[const.DAY_COLUMN]
    date_text: pd.Series = days.dt.strftime(const.DATE_FORMAT)
    values: pd.Series = sorted_rows[source_column]
    table_data: Dict[str, list] = {
        const.DATE_COLUMN: date_text.tolist(),
        output_column: values.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_by_range(daily: pd.DataFrame, source_column: str, output_column: str) -> Dict[str, Dict[str, pd.DataFrame]]:
    result: Dict[str, Dict[str, pd.DataFrame]] = {}

    for range_label in const.DATE_RANGES:
        tables_by_subject: Dict[str, pd.DataFrame] = {}

        for subject in const.SUBJECTS:
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
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        last_name: str = getattr(row, const.LAST_NAME_COLUMN)
        first_name: str = getattr(row, const.FIRST_NAME_COLUMN)
        full_name: str = const.FULL_NAME_TEMPLATE.format(last_name=last_name, first_name=first_name)
        pair: Tuple[str, str] = (subject_key, user)
        names[pair] = full_name

    return names

def build_student_catalog() -> Dict[str, Dict[str, str]]:
    participation: pd.DataFrame = load_participation()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    names: Dict[Tuple[str, str], str] = build_names(participation=participation)
    is_enrolled: pd.Series = enrollment_cross[const.ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    catalog: Dict[str, Dict[str, str]] = {}

    for subject in const.SUBJECTS:
        subject_key: str = const.SUBJECT_KEYS[subject]
        is_subject: pd.Series = enrolled_rows[const.SUBJECT_COLUMN] == subject_key
        subject_rows: pd.DataFrame = enrolled_rows.loc[is_subject]
        users: List[str] = sorted(subject_rows[const.USER_COLUMN].tolist())
        labels_to_users: Dict[str, str] = {}

        for user in users:
            pair: Tuple[str, str] = (subject_key, user)
            full_name: str = names[pair]
            label: str = const.STUDENT_LABEL_TEMPLATE.format(user=user, full_name=full_name)
            labels_to_users[label] = user

        catalog[subject] = labels_to_users

    return catalog

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_PARTICIPATION)
def build_all() -> Dict[str, Dict[str, object]]:
    daily: pd.DataFrame = build_daily_table()
    activity: Dict[str, Dict[str, pd.DataFrame]] = build_by_range(
        daily=daily, source_column=const.INTERACTIONS_COLUMN, output_column=const.ACTIVITIES_COLUMN)
    accesses: Dict[str, Dict[str, pd.DataFrame]] = build_by_range(
        daily=daily, source_column=const.ACCESSES_COLUMN, output_column=const.ACCESSES_COLUMN)
    catalog: Dict[str, Dict[str, str]] = build_student_catalog()
    result: Dict[str, Dict[str, object]] = {
        const.ACTIVITY_KEY: activity,
        const.ACCESSES_COLUMN: accesses,
        const.CATALOG_KEY: catalog,
    }

    return result

def get_subject_options() -> List[str]:
    options: List[str] = [const.SUBJECT_ALL]
    options.extend(const.SUBJECTS)

    return options

def sum_subjects(tables_by_subject: Dict[str, pd.DataFrame], value_column: str) -> pd.DataFrame:
    tables: List[pd.DataFrame] = list(tables_by_subject.values())
    combined: pd.DataFrame = pd.concat(tables, ignore_index=True)
    grouped: pd.Series = combined.groupby(const.DATE_COLUMN)[value_column].sum()
    sorted_values: pd.Series = grouped.sort_index()
    result: pd.DataFrame = sorted_values.reset_index()

    return result

def get_student_options(subject: str) -> List[str]:
    if subject == const.SUBJECT_ALL:
        return [const.STUDENT_ALL]

    catalog: Dict[str, Dict[str, str]] = build_all()[const.CATALOG_KEY]
    labels_to_users: Dict[str, str] = catalog[subject]
    labels: List[str] = list(labels_to_users.keys())
    options: List[str] = [const.STUDENT_ALL]
    options.extend(labels)

    return options

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_STUDENT_ACTIVITY)
def build_student_daily(subject: str, student: str, range_label: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    catalog: Dict[str, Dict[str, str]] = build_all()[const.CATALOG_KEY]
    labels_to_users: Dict[str, str] = catalog[subject]
    user: str = labels_to_users[student]
    traceability: pd.DataFrame = load_enrolled_traceability()
    is_subject: pd.Series = traceability[const.SUBJECT_COLUMN] == subject_key
    is_user: pd.Series = traceability[const.USER_COLUMN] == user
    mask: pd.Series = is_subject & is_user
    rows: pd.DataFrame = traceability.loc[mask]
    start: pd.Timestamp = window_start(range_label=range_label)
    days: pd.DatetimeIndex = pd.date_range(start=start, end=const.ANCHOR_DATE, freq=const.DAILY_FREQUENCY)
    interactions_by_day: pd.Series = rows.groupby(const.DAY_COLUMN).size()
    is_entry: pd.Series = rows[const.ENTRY_COLUMN]
    entry_rows: pd.DataFrame = rows.loc[is_entry]
    entries_by_day: pd.Series = entry_rows.groupby(const.DAY_COLUMN).size()
    interactions: pd.Series = interactions_by_day.reindex(days, fill_value=0)
    entries: pd.Series = entries_by_day.reindex(days, fill_value=0)
    date_text: List[str] = days.strftime(const.DATE_FORMAT).tolist()
    table_data: Dict[str, list] = {
        const.DATE_COLUMN: date_text,
        const.ACTIVITIES_COLUMN: interactions.tolist(),
        const.ACCESSES_COLUMN: entries.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def get_activity(subject: str, date_range: str, student: str) -> pd.DataFrame:
    result: pd.DataFrame

    if student == const.STUDENT_ALL:
        activity_by_date: Dict[str, Dict[str, pd.DataFrame]] = build_all()[const.ACTIVITY_KEY]
        activity_of_range: Dict[str, pd.DataFrame] = activity_by_date[date_range]
        if subject == const.SUBJECT_ALL:
            result = sum_subjects(activity_of_range, const.ACTIVITIES_COLUMN)
        else:
            result = activity_of_range[subject]
    else:
        daily: pd.DataFrame = build_student_daily(subject=subject, student=student, range_label=date_range)
        columns: List[str] = [const.DATE_COLUMN, const.ACTIVITIES_COLUMN]
        result = daily[columns]

    return result

def get_accesses(subject: str, date_range: str, student: str) -> pd.DataFrame:
    result: pd.DataFrame

    if student == const.STUDENT_ALL:
        access_evolution: Dict[str, Dict[str, pd.DataFrame]] = build_all()[const.ACCESSES_COLUMN]
        accesses_of_range: Dict[str, pd.DataFrame] = access_evolution[date_range]
        if subject == const.SUBJECT_ALL:
            result = sum_subjects(accesses_of_range, const.ACCESSES_COLUMN)
        else:
            result = accesses_of_range[subject]
    else:
        daily: pd.DataFrame = build_student_daily(subject=subject, student=student, range_label=date_range)
        columns: List[str] = [const.DATE_COLUMN, const.ACCESSES_COLUMN]
        result = daily[columns]

    return result
