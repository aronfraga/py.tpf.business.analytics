from functools import reduce
from typing import Dict, List

import pandas as pd

from data.real_common import (
    SUBJECT_ALL,
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrolled_traceability,
    sum_tables,
)
from kpis.kpis_trazabilidad import (
    actividad_por_dia_y_franja,
    interacciones_diarias,
    interacciones_por_tipo,
    matriz_dia_franja,
)

SUBJECT_COLUMN: str = "materia"
TYPE_COLUMN: str = "tipo"
INTERACTIONS_COLUMN: str = "interacciones"
DAY_COLUMN: str = "dia"
ACTION_COLUMN: str = "action"
COUNT_COLUMN: str = "count"
DATE_COLUMN: str = "date"
TIMELINE_COLUMN: str = "interactions"
DATE_FORMAT: str = "%Y-%m-%d"

DAY_LABELS: Dict[str, str] = {
    "lunes": "Lun",
    "martes": "Mar",
    "miércoles": "Mié",
    "jueves": "Jue",
    "viernes": "Vie",
    "sábado": "Sáb",
    "domingo": "Dom",
}

def build_interactions_by_action(by_type: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = by_type[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = by_type.loc[is_subject]
    types: List[str] = selected[TYPE_COLUMN].tolist()
    counts: List[int] = selected[INTERACTIONS_COLUMN].tolist()
    table_data: Dict[str, list] = {
        ACTION_COLUMN: types,
        COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_heatmap(activity: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    matrix: pd.DataFrame = matriz_dia_franja(actividad=activity, materia=subject_key)
    renamed: pd.DataFrame = matrix.rename(index=DAY_LABELS)
    renamed.columns.name = None
    renamed.index.name = None

    return renamed

def build_timeline(daily: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = daily[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = daily.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(DAY_COLUMN)
    days: pd.Series = sorted_rows[DAY_COLUMN]
    date_text: pd.Series = days.dt.strftime(DATE_FORMAT)
    values: pd.Series = sorted_rows[INTERACTIONS_COLUMN]
    table_data: Dict[str, list] = {
        DATE_COLUMN: date_text.tolist(),
        TIMELINE_COLUMN: values.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_all_by_action(by_action: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    summed: pd.DataFrame = sum_tables(list(by_action.values()), [ACTION_COLUMN], [COUNT_COLUMN])
    result: pd.DataFrame = summed.sort_values(COUNT_COLUMN, ascending=False).reset_index(drop=True)

    return result

def build_all_heatmap(heatmaps: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    result: pd.DataFrame = reduce(lambda left, right: left.add(right, fill_value=0), heatmaps.values()).astype(int)

    return result

def build_all_timeline(timelines: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    summed: pd.DataFrame = sum_tables(list(timelines.values()), [DATE_COLUMN], [TIMELINE_COLUMN])
    result: pd.DataFrame = summed.sort_values(DATE_COLUMN).reset_index(drop=True)

    return result

def build_all() -> Dict[str, Dict[str, pd.DataFrame]]:
    traceability: pd.DataFrame = load_enrolled_traceability()
    by_type: pd.DataFrame = interacciones_por_tipo(df=traceability)
    activity: pd.DataFrame = actividad_por_dia_y_franja(df=traceability)
    daily: pd.DataFrame = interacciones_diarias(df=traceability)
    by_action: Dict[str, pd.DataFrame] = {}
    heatmaps: Dict[str, pd.DataFrame] = {}
    timelines: Dict[str, pd.DataFrame] = {}

    for subject in SUBJECTS:
        by_action[subject] = build_interactions_by_action(by_type=by_type, subject=subject)
        heatmaps[subject] = build_heatmap(activity=activity, subject=subject)
        timelines[subject] = build_timeline(daily=daily, subject=subject)

    by_action[SUBJECT_ALL] = build_all_by_action(by_action=by_action)
    heatmaps[SUBJECT_ALL] = build_all_heatmap(heatmaps=heatmaps)
    timelines[SUBJECT_ALL] = build_all_timeline(timelines=timelines)

    result: Dict[str, Dict[str, pd.DataFrame]] = {
        "by_action": by_action,
        "heatmap": heatmaps,
        "timeline": timelines,
    }

    return result

ALL_TABLES: Dict[str, Dict[str, pd.DataFrame]] = build_all()

INTERACTIONS_BY_ACTION: Dict[str, pd.DataFrame] = ALL_TABLES["by_action"]

ACTIVITY_HEATMAP: Dict[str, pd.DataFrame] = ALL_TABLES["heatmap"]

TIMELINE: Dict[str, pd.DataFrame] = ALL_TABLES["timeline"]
