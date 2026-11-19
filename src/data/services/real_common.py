from typing import List
from data.kpis.kpis_trazabilidad import cargar_trazabilidad, marcar_ingresos
import pandas as pd
import streamlit as st
import constants as const

def select_subject(frame: pd.DataFrame, column: str, subject: str) -> pd.DataFrame:
    if subject == const.SUBJECT_ALL:
        return frame

    is_subject: pd.Series = frame[column] == const.SUBJECT_KEYS[subject]
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

    if range_label == const.RANGE_ALL:
        result = const.DATA_START_DATE
    else:
        days: int = const.RANGE_DAYS[range_label]
        offset_days: int = days - 1
        offset: pd.Timedelta = pd.Timedelta(days=offset_days)
        result = const.ANCHOR_DATE - offset

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_LOAD_PARTICIPATION)
def load_participation() -> pd.DataFrame:
    file_path: Path = const.INTEGRATED_PATH / const.PARTICIPATION_FILE
    participation: pd.DataFrame = pd.read_parquet(file_path)

    return participation

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_LOAD_GRADES)
def load_grades() -> pd.DataFrame:
    file_path: Path = const.INTEGRATED_PATH / const.GRADES_FILE
    grades: pd.DataFrame = pd.read_parquet(file_path)

    return grades

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_LOAD_ENROLLMENT_CROSS)
def load_enrollment_cross() -> pd.DataFrame:
    file_path: Path = const.INTEGRATED_PATH / const.ENROLLMENT_CROSS_FILE
    cross: pd.DataFrame = pd.read_parquet(file_path)

    return cross

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_LOAD_ENROLLMENT_LIST)
def load_enrollment_list() -> pd.DataFrame:
    file_path: Path = const.INTEGRATED_PATH / const.ENROLLMENT_LIST_FILE
    enrollment_list: pd.DataFrame = pd.read_parquet(file_path)

    return enrollment_list

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_LOAD_TRACEABILITY_ALL)
def load_all_traceability() -> pd.DataFrame:
    only_enrolled: bool = False
    loaded: pd.DataFrame = cargar_trazabilidad(datos=const.DATA_PATH, solo_matriculados=only_enrolled)
    marked: pd.DataFrame = marcar_ingresos(df=loaded, minutos_inactividad=const.INACTIVITY_MINUTES)

    return marked

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_LOAD_TRACEABILITY_ENROLLED)
def load_enrolled_traceability() -> pd.DataFrame:
    only_enrolled: bool = True
    loaded: pd.DataFrame = cargar_trazabilidad(datos=const.DATA_PATH, solo_matriculados=only_enrolled)
    marked: pd.DataFrame = marcar_ingresos(df=loaded, minutos_inactividad=const.INACTIVITY_MINUTES)

    return marked
