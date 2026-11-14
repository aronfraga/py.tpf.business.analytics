from typing import Dict, List

import pandas as pd

from data.real_common import (
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrollment_cross,
    load_grades,
)
from kpis.kpis_calificaciones import condicion_academica, distribucion_de_notas

SUBJECT_COLUMN: str = "materia"
USER_COLUMN: str = "usuario"
INSTRUMENT_SOURCE_COLUMN: str = "instrumento"
FILE_ID_COLUMN: str = "id_archivo"
OBTAINED_COLUMN: str = "nota_obtenida"
MAXIMUM_COLUMN: str = "nota_max"
PERCENT_COLUMN: str = "percent"
ENROLLED_COLUMN: str = "matriculado"
INSTRUMENT_COLUMN: str = "instrument"
AVERAGE_COLUMN: str = "average"
RANGE_COLUMN: str = "range"
COUNT_COLUMN: str = "count"
STATUS_COLUMN: str = "status"
HISTOGRAM_SOURCE_RANGE_COLUMN: str = "rango"
HISTOGRAM_SOURCE_FROM_COLUMN: str = "desde"
HISTOGRAM_SOURCE_TO_COLUMN: str = "hasta"
HISTOGRAM_SOURCE_COUNT_COLUMN: str = "estudiantes"
CONDITION_COLUMN: str = "condicion"
CONDITION_COUNT_COLUMN: str = "estudiantes"

PERCENT_FACTOR: float = 100.0
SCALE_DIVISOR: int = 10
AVERAGE_DECIMALS: int = 1
HISTOGRAM_BIN_WIDTH: int = 10

STATUS_LABELS: Dict[str, str] = {
    "libre": "Libre",
    "regular": "Regular",
    "promocionado": "Promociona",
}

STATUS_ORDER: List[str] = ["libre", "regular", "promocionado"]

def build_instrument_table(grades: pd.DataFrame, enrollment_cross: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    pair_columns: list = [SUBJECT_COLUMN, USER_COLUMN]
    is_enrolled: pd.Series = enrollment_cross[ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    enrolled_pairs: pd.DataFrame = enrolled_rows[pair_columns]
    joined: pd.DataFrame = grades.merge(enrolled_pairs, on=pair_columns, how="inner")
    has_maximum: pd.Series = joined[MAXIMUM_COLUMN] > 0
    is_subject: pd.Series = joined[SUBJECT_COLUMN] == subject_key
    mask: pd.Series = has_maximum & is_subject
    selected: pd.DataFrame = joined.loc[mask].copy()
    ratio: pd.Series = selected[OBTAINED_COLUMN] / selected[MAXIMUM_COLUMN]
    selected[PERCENT_COLUMN] = ratio * PERCENT_FACTOR
    grouped: pd.core.groupby.DataFrameGroupBy = selected.groupby(INSTRUMENT_SOURCE_COLUMN)
    mean_percent: pd.Series = grouped[PERCENT_COLUMN].mean()
    first_file: pd.Series = grouped[FILE_ID_COLUMN].min()
    summary: pd.DataFrame = pd.DataFrame({AVERAGE_COLUMN: mean_percent, FILE_ID_COLUMN: first_file})
    ordered: pd.DataFrame = summary.sort_values(FILE_ID_COLUMN)
    scaled: pd.Series = ordered[AVERAGE_COLUMN] / SCALE_DIVISOR
    rounded: pd.Series = scaled.round(AVERAGE_DECIMALS)
    instruments: List[str] = ordered.index.tolist()
    table_data: Dict[str, list] = {
        INSTRUMENT_COLUMN: instruments,
        AVERAGE_COLUMN: rounded.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_range_label(row_from: int, row_to: int) -> str:
    label_from: int = row_from // SCALE_DIVISOR
    label_to: int = row_to // SCALE_DIVISOR
    label: str = f"{label_from}-{label_to}"

    return label

def build_histogram_table(distribution: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = distribution[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = distribution.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(HISTOGRAM_SOURCE_FROM_COLUMN)
    labels: List[str] = []

    for row in sorted_rows.itertuples(index=False):
        row_from: int = getattr(row, HISTOGRAM_SOURCE_FROM_COLUMN)
        row_to: int = getattr(row, HISTOGRAM_SOURCE_TO_COLUMN)
        label: str = build_range_label(row_from=row_from, row_to=row_to)
        labels.append(label)

    counts: List[int] = sorted_rows[HISTOGRAM_SOURCE_COUNT_COLUMN].tolist()
    table_data: Dict[str, list] = {
        RANGE_COLUMN: labels,
        COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_status_table(conditions: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = conditions[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = conditions.loc[is_subject]
    labels: List[str] = []
    counts: List[int] = []

    for condition in STATUS_ORDER:
        is_condition: pd.Series = selected[CONDITION_COLUMN] == condition
        condition_rows: pd.DataFrame = selected.loc[is_condition]
        condition_count: int = int(condition_rows[CONDITION_COUNT_COLUMN].sum())
        label: str = STATUS_LABELS[condition]
        labels.append(label)
        counts.append(condition_count)

    table_data: Dict[str, list] = {
        STATUS_COLUMN: labels,
        COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_all() -> Dict[str, Dict[str, pd.DataFrame]]:
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    distribution: pd.DataFrame = distribucion_de_notas(
        calificaciones=grades,
        cruce=enrollment_cross,
        ancho_bin=HISTOGRAM_BIN_WIDTH,
        matriculados=True,
    )
    conditions: pd.DataFrame = condicion_academica(
        calificaciones=grades,
        cruce=enrollment_cross,
        matriculados=True,
    )
    instruments: Dict[str, pd.DataFrame] = {}
    histograms: Dict[str, pd.DataFrame] = {}
    statuses: Dict[str, pd.DataFrame] = {}

    for subject in SUBJECTS:
        instruments[subject] = build_instrument_table(grades=grades, enrollment_cross=enrollment_cross, subject=subject)
        histograms[subject] = build_histogram_table(distribution=distribution, subject=subject)
        statuses[subject] = build_status_table(conditions=conditions, subject=subject)

    result: Dict[str, Dict[str, pd.DataFrame]] = {
        "instruments": instruments,
        "histogram": histograms,
        "status": statuses,
    }

    return result

ALL_TABLES: Dict[str, Dict[str, pd.DataFrame]] = build_all()

INSTRUMENT_COMPARISON: Dict[str, pd.DataFrame] = ALL_TABLES["instruments"]

GRADE_HISTOGRAM: Dict[str, pd.DataFrame] = ALL_TABLES["histogram"]

COURSE_STATUS: Dict[str, pd.DataFrame] = ALL_TABLES["status"]
