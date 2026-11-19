from typing import Dict, List
from data.real_common import load_enrollment_cross, load_grades, select_subject
from kpis.kpis_calificaciones import condicion_academica, distribucion_de_notas
import pandas as pd
import streamlit as st
import constants as const

def build_instrument_table(grades: pd.DataFrame, enrollment_cross: pd.DataFrame, subject: str) -> pd.DataFrame:
    pair_columns: list = [const.SUBJECT_COLUMN, const.USER_COLUMN]
    is_enrolled: pd.Series = enrollment_cross[const.ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    enrolled_pairs: pd.DataFrame = enrolled_rows[pair_columns]
    joined: pd.DataFrame = grades.merge(enrolled_pairs, on=pair_columns, how="inner")
    has_maximum: pd.Series = joined[const.MAXIMUM_COLUMN] > 0
    with_maximum: pd.DataFrame = joined.loc[has_maximum]
    selected: pd.DataFrame = select_subject(with_maximum, const.SUBJECT_COLUMN, subject).copy()
    ratio: pd.Series = selected[const.OBTAINED_COLUMN] / selected[const.MAXIMUM_COLUMN]
    selected[const.PERFORMANCE_PERCENT_COLUMN] = ratio * const.PERCENT_FACTOR
    grouped: pd.core.groupby.DataFrameGroupBy = selected.groupby(const.INSTRUMENT_SOURCE_COLUMN)
    mean_percent: pd.Series = grouped[const.PERFORMANCE_PERCENT_COLUMN].mean()
    first_file: pd.Series = grouped[const.FILE_ID_COLUMN].min()
    summary: pd.DataFrame = pd.DataFrame({const.AVERAGE_COLUMN: mean_percent, const.FILE_ID_COLUMN: first_file})
    ordered: pd.DataFrame = summary.sort_values(const.FILE_ID_COLUMN)
    scaled: pd.Series = ordered[const.AVERAGE_COLUMN] / const.SCALE_DIVISOR
    rounded: pd.Series = scaled.round(const.AVERAGE_DECIMALS)
    instruments: List[str] = ordered.index.tolist()
    table_data: Dict[str, list] = {
        const.INSTRUMENT_COLUMN: instruments,
        const.AVERAGE_COLUMN: rounded.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_range_label(row_from: int, row_to: int) -> str:
    label_from: int = row_from // const.SCALE_DIVISOR
    label_to: int = row_to // const.SCALE_DIVISOR
    label: str = const.RANGE_LABEL_TEMPLATE.format(start=label_from, end=label_to)

    return label

def build_histogram_table(distribution: pd.DataFrame, subject: str) -> pd.DataFrame:
    selected: pd.DataFrame = select_subject(distribution, const.SUBJECT_COLUMN, subject)
    range_columns: list = [const.DISTRIBUTION_FROM_COLUMN, const.DISTRIBUTION_TO_COLUMN]
    grouped_rows: pd.DataFrame = selected.groupby(range_columns, as_index=False)[const.STUDENTS_COLUMN].sum()
    sorted_rows: pd.DataFrame = grouped_rows.sort_values(const.DISTRIBUTION_FROM_COLUMN)
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

def build_status_table(conditions: pd.DataFrame, subject: str, enrolled_count: int) -> pd.DataFrame:
    selected: pd.DataFrame = select_subject(conditions, const.SUBJECT_COLUMN, subject)
    labels: List[str] = []
    counts: List[int] = []

    for condition in const.STATUS_ORDER:
        is_condition: pd.Series = selected[const.CONDITION_COLUMN] == condition
        condition_rows: pd.DataFrame = selected.loc[is_condition]
        condition_count: int = int(condition_rows[const.STUDENTS_COLUMN].sum())
        label: str = const.CONDITION_LABELS[condition]
        labels.append(label)
        counts.append(condition_count)

    not_presented_count: int = enrolled_count - sum(counts)
    labels.append(const.NOT_PRESENTED_LABEL)
    counts.append(not_presented_count)

    table_data: Dict[str, list] = {
        const.STATUS_COLUMN: labels,
        const.COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_PERFORMANCE)
def build_all() -> Dict[str, Dict[str, pd.DataFrame]]:
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    distribution: pd.DataFrame = distribucion_de_notas(
        calificaciones=grades, cruce=enrollment_cross, ancho_bin=const.HISTOGRAM_BIN_WIDTH, matriculados=True)
    conditions: pd.DataFrame = condicion_academica(calificaciones=grades, cruce=enrollment_cross, matriculados=True)
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[enrollment_cross[const.ENROLLED_COLUMN]]
    enrolled_by_subject: pd.Series = enrolled_rows.groupby(const.SUBJECT_COLUMN).size()
    instruments: Dict[str, pd.DataFrame] = {}
    histograms: Dict[str, pd.DataFrame] = {}
    statuses: Dict[str, pd.DataFrame] = {}

    for subject in const.SUBJECT_OPTIONS:
        instruments[subject] = build_instrument_table(grades=grades, enrollment_cross=enrollment_cross, subject=subject)
        histograms[subject] = build_histogram_table(distribution=distribution, subject=subject)
        subject_enrolled: int = int(enrolled_by_subject.sum()) if subject == const.SUBJECT_ALL else int(
            enrolled_by_subject[const.SUBJECT_KEYS[subject]])
        statuses[subject] = build_status_table(conditions=conditions, subject=subject, enrolled_count=subject_enrolled)

    by_subject_tables: List[pd.DataFrame] = []

    for subject in const.SUBJECTS:
        by_subject_tables.append(instruments[subject].assign(**{const.SUBJECT_NAME_COLUMN: subject}))

    instruments[const.SUBJECT_ALL] = pd.concat(by_subject_tables, ignore_index=True)

    result: Dict[str, Dict[str, pd.DataFrame]] = {
        const.INSTRUMENTS_KEY: instruments,
        const.HISTOGRAM_KEY: histograms,
        const.STATUS_COLUMN: statuses,
    }

    return result
