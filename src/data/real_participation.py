from typing import Dict

import pandas as pd

from data.real_common import (
    ALGEBRA,
    ALGORITHMS,
    DATE_RANGES,
    PROBABILITY,
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrolled_traceability,
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

PARTICIPATION_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "La actividad crece de forma sostenida desde el inicio del período y cae de "
        "manera marcada los fines de semana. Los accesos acompañan la misma "
        "tendencia."
    ),
    ALGORITHMS: (
        "Es la asignatura con mayor actividad. El pico de las últimas semanas "
        "coincide con las entregas de trabajos prácticos."
    ),
    PROBABILITY: (
        "La actividad es la más baja de las tres asignaturas, aunque mantiene una "
        "tendencia creciente. Se observa una caída leve en octubre."
    ),
}
