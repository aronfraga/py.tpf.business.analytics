from functools import reduce
from typing import Dict, List
from data.services.real_common import load_enrolled_traceability, sum_tables
from data.kpis.kpis_trazabilidad import (actividad_por_dia_y_franja, interacciones_diarias, interacciones_por_tipo, matriz_dia_franja)
import pandas as pd
import streamlit as st
import constants as const

def build_interactions_by_action(by_type: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = by_type[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = by_type.loc[is_subject]
    types: List[str] = selected[const.TYPE_COLUMN].tolist()
    counts: List[int] = selected[const.INTERACTIONS_COLUMN].tolist()
    table_data: Dict[str, list] = {
        const.ACTION_COLUMN: types,
        const.COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_heatmap(activity: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    matrix: pd.DataFrame = matriz_dia_franja(actividad=activity, materia=subject_key)
    renamed: pd.DataFrame = matrix.rename(index=const.WEEKDAY_SHORT_LABELS)
    renamed.columns.name = None
    renamed.index.name = None

    return renamed

def build_timeline(daily: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = const.SUBJECT_KEYS[subject]
    is_subject: pd.Series = daily[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = daily.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(const.DAY_COLUMN)
    days: pd.Series = sorted_rows[const.DAY_COLUMN]
    date_text: pd.Series = days.dt.strftime(const.DATE_FORMAT)
    values: pd.Series = sorted_rows[const.INTERACTIONS_COLUMN]
    table_data: Dict[str, list] = {
        const.DATE_COLUMN: date_text.tolist(),
        const.TIMELINE_COLUMN: values.tolist(),
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_all_by_action(by_action: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    summed: pd.DataFrame = sum_tables(list(by_action.values()), [const.ACTION_COLUMN], [const.COUNT_COLUMN])
    result: pd.DataFrame = summed.sort_values(const.COUNT_COLUMN, ascending=False).reset_index(drop=True)

    return result

def build_all_heatmap(heatmaps: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    result: pd.DataFrame = reduce(lambda left, right: left.add(right, fill_value=0), heatmaps.values()).astype(int)

    return result

def build_all_timeline(timelines: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    summed: pd.DataFrame = sum_tables(list(timelines.values()), [const.DATE_COLUMN], [const.TIMELINE_COLUMN])
    result: pd.DataFrame = summed.sort_values(const.DATE_COLUMN).reset_index(drop=True)

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_TRACEABILITY)
def build_all() -> Dict[str, Dict[str, pd.DataFrame]]:
    traceability: pd.DataFrame = load_enrolled_traceability()
    by_type: pd.DataFrame = interacciones_por_tipo(df=traceability)
    activity: pd.DataFrame = actividad_por_dia_y_franja(df=traceability)
    daily: pd.DataFrame = interacciones_diarias(df=traceability)
    by_action: Dict[str, pd.DataFrame] = {}
    heatmaps: Dict[str, pd.DataFrame] = {}
    timelines: Dict[str, pd.DataFrame] = {}

    for subject in const.SUBJECTS:
        by_action[subject] = build_interactions_by_action(by_type=by_type, subject=subject)
        heatmaps[subject] = build_heatmap(activity=activity, subject=subject)
        timelines[subject] = build_timeline(daily=daily, subject=subject)

    by_action[const.SUBJECT_ALL] = build_all_by_action(by_action=by_action)
    heatmaps[const.SUBJECT_ALL] = build_all_heatmap(heatmaps=heatmaps)
    timelines[const.SUBJECT_ALL] = build_all_timeline(timelines=timelines)

    result: Dict[str, Dict[str, pd.DataFrame]] = {
        const.BY_ACTION_KEY: by_action,
        const.HEATMAP_KEY: heatmaps,
        const.TIMELINE_KEY: timelines,
    }

    return result
