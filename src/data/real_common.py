from typing import List

import pandas as pd
import streamlit as st

from kpis.kpis_trazabilidad import cargar_trazabilidad, marcar_ingresos
from constants import (
    ANCHOR_DATE,
    CACHE_TTL_SECONDS,
    DATA_PATH,
    DATA_START_DATE,
    ENROLLMENT_CROSS_FILE,
    ENROLLMENT_LIST_FILE,
    GRADES_FILE,
    INACTIVITY_MINUTES,
    INTEGRATED_PATH,
    PARTICIPATION_FILE,
    RANGE_ALL,
    RANGE_DAYS,
    SPINNER_LOAD_ENROLLMENT_CROSS,
    SPINNER_LOAD_ENROLLMENT_LIST,
    SPINNER_LOAD_GRADES,
    SPINNER_LOAD_PARTICIPATION,
    SPINNER_LOAD_TRACEABILITY_ALL,
    SPINNER_LOAD_TRACEABILITY_ENROLLED,
    SUBJECT_ALL,
    SUBJECT_KEYS,
)

def select_subject(frame: pd.DataFrame, column: str, subject: str) -> pd.DataFrame:
    if subject == SUBJECT_ALL:
        return frame

    is_subject: pd.Series = frame[column] == SUBJECT_KEYS[subject]
    result: pd.DataFrame = frame.loc[is_subject]

    return result

def sort_by_id_asc(table: pd.DataFrame, id_column: str) -> pd.DataFrame:
    result: pd.DataFrame = table.sort_values(by=id_column, ascending=True, kind="stable").reset_index(drop=True)

    return result

def sum_tables(tables: List[pd.DataFrame], key_columns: List[str], value_columns: List[str]) -> pd.DataFrame:
    combined: pd.DataFrame = pd.concat(tables, ignore_index=True)
    grouped: pd.DataFrame = combined.groupby(key_columns, sort=False, as_index=False)[value_columns].sum()

    return grouped

def window_start(range_label: str) -> pd.Timestamp:
    result: pd.Timestamp

    if range_label == RANGE_ALL:
        result = DATA_START_DATE
    else:
        days: int = RANGE_DAYS[range_label]
        offset_days: int = days - 1
        offset: pd.Timedelta = pd.Timedelta(days=offset_days)
        result = ANCHOR_DATE - offset

    return result

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_LOAD_PARTICIPATION)
def load_participation() -> pd.DataFrame:
    file_path: Path = INTEGRATED_PATH / PARTICIPATION_FILE
    participation: pd.DataFrame = pd.read_parquet(file_path)

    return participation

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_LOAD_GRADES)
def load_grades() -> pd.DataFrame:
    file_path: Path = INTEGRATED_PATH / GRADES_FILE
    grades: pd.DataFrame = pd.read_parquet(file_path)

    return grades

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_LOAD_ENROLLMENT_CROSS)
def load_enrollment_cross() -> pd.DataFrame:
    file_path: Path = INTEGRATED_PATH / ENROLLMENT_CROSS_FILE
    cross: pd.DataFrame = pd.read_parquet(file_path)

    return cross

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_LOAD_ENROLLMENT_LIST)
def load_enrollment_list() -> pd.DataFrame:
    file_path: Path = INTEGRATED_PATH / ENROLLMENT_LIST_FILE
    enrollment_list: pd.DataFrame = pd.read_parquet(file_path)

    return enrollment_list

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_LOAD_TRACEABILITY_ALL)
def load_all_traceability() -> pd.DataFrame:
    only_enrolled: bool = False
    loaded: pd.DataFrame = cargar_trazabilidad(datos=DATA_PATH, solo_matriculados=only_enrolled)
    marked: pd.DataFrame = marcar_ingresos(df=loaded, minutos_inactividad=INACTIVITY_MINUTES)

    return marked

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_LOAD_TRACEABILITY_ENROLLED)
def load_enrolled_traceability() -> pd.DataFrame:
    only_enrolled: bool = True
    loaded: pd.DataFrame = cargar_trazabilidad(datos=DATA_PATH, solo_matriculados=only_enrolled)
    marked: pd.DataFrame = marcar_ingresos(df=loaded, minutos_inactividad=INACTIVITY_MINUTES)

    return marked
