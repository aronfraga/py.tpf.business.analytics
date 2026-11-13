from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st

from kpis.kpis_trazabilidad import cargar_trazabilidad, marcar_ingresos

ALGEBRA: str = "Álgebra"
ALGORITHMS: str = "Algoritmos y Estructuras de Datos"
PROBABILITY: str = "Probabilidad y Estadística"

SUBJECTS: List[str] = [ALGEBRA, ALGORITHMS, PROBABILITY]

ALGEBRA_KEY: str = "algebra"
ALGORITHMS_KEY: str = "algoritmos"
PROBABILITY_KEY: str = "probabilidad"

SUBJECT_KEYS: Dict[str, str] = {
    ALGEBRA: ALGEBRA_KEY,
    ALGORITHMS: ALGORITHMS_KEY,
    PROBABILITY: PROBABILITY_KEY,
}

KEY_SUBJECTS: Dict[str, str] = {
    ALGEBRA_KEY: ALGEBRA,
    ALGORITHMS_KEY: ALGORITHMS,
    PROBABILITY_KEY: PROBABILITY,
}

RANGE_ALL: str = "Todo el período"
RANGE_4_WEEKS: str = "Últimas 4 semanas"
RANGE_2_WEEKS: str = "Últimas 2 semanas"

DATE_RANGES: List[str] = [RANGE_ALL, RANGE_4_WEEKS, RANGE_2_WEEKS]

DAYS_4_WEEKS: int = 28
DAYS_2_WEEKS: int = 14

RANGE_DAYS: Dict[str, int] = {
    RANGE_4_WEEKS: DAYS_4_WEEKS,
    RANGE_2_WEEKS: DAYS_2_WEEKS,
}

ANCHOR_DATE: pd.Timestamp = pd.Timestamp("2025-10-24")
DATA_START_DATE: pd.Timestamp = pd.Timestamp("2025-08-05")

CURRENT_FILE: Path = Path(__file__)
RESOLVED_FILE: Path = CURRENT_FILE.resolve()
PROJECT_ROOT: Path = RESOLVED_FILE.parents[2]
DATA_PATH: Path = PROJECT_ROOT / "data"

INACTIVITY_MINUTES: int = 30

INTEGRATED_PATH: Path = DATA_PATH / "integrado"
PARTICIPATION_FILE: str = "participacion_integrado.parquet"
GRADES_FILE: str = "calificaciones_integrado.parquet"
ENROLLMENT_CROSS_FILE: str = "cruce_matriculados_integrado.parquet"

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

@st.cache_data
def load_participation() -> pd.DataFrame:
    file_path: Path = INTEGRATED_PATH / PARTICIPATION_FILE
    participation: pd.DataFrame = pd.read_parquet(file_path)

    return participation

@st.cache_data
def load_grades() -> pd.DataFrame:
    file_path: Path = INTEGRATED_PATH / GRADES_FILE
    grades: pd.DataFrame = pd.read_parquet(file_path)

    return grades

@st.cache_data
def load_enrollment_cross() -> pd.DataFrame:
    file_path: Path = INTEGRATED_PATH / ENROLLMENT_CROSS_FILE
    cross: pd.DataFrame = pd.read_parquet(file_path)

    return cross

@st.cache_data
def load_enrolled_traceability() -> pd.DataFrame:
    only_enrolled: bool = True
    loaded: pd.DataFrame = cargar_trazabilidad(datos=DATA_PATH, solo_matriculados=only_enrolled)
    marked: pd.DataFrame = marcar_ingresos(df=loaded, minutos_inactividad=INACTIVITY_MINUTES)

    return marked
