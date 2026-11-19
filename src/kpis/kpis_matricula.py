import sys
from pathlib import Path

import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[1])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
from constants import (
    CONDITION_COLUMN,
    CONDITION_DROPPED,
    CONDITION_NOT_PRESENTED,
    ENROLLED_ACTIVE_COLUMN,
    ENROLLED_COLUMN,
    ENROLLMENT_STATE_COLUMN,
    ENROLLMENT_STATE_DROPPED,
    INTERACTIONS_COLUMN,
    KEY_COLUMNS,
    NOT_ENROLLED_ACTIVE_COLUMN,
    PERCENTAGE_COLUMN,
    PERCENT_FACTOR,
    ROUND_DECIMALS,
    SITUATIONS,
    SITUATION_COLUMN,
    SITUATION_GENERAL,
    STUDENTS_COLUMN,
    SUBJECT_COLUMN,
)

try:
    from .kpis_calificaciones import condicion_por_estudiante
except ImportError:
    from kpis_calificaciones import condicion_por_estudiante


CLAVES = KEY_COLUMNS
SITUACIONES = SITUATIONS


def estudiantes_activos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    activos = participacion.loc[participacion[INTERACTIONS_COLUMN] > 0, CLAVES]
    res = activos.merge(cruce[CLAVES + [ENROLLED_COLUMN]], on=CLAVES, how="left")
    res[ENROLLED_COLUMN] = res[ENROLLED_COLUMN].fillna(False).astype(bool)
    return res.sort_values(CLAVES).reset_index(drop=True)


def resumen_activos_por_matricula(activos: pd.DataFrame) -> pd.DataFrame:
    return (
        activos.groupby([SUBJECT_COLUMN, ENROLLED_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=[True, False], fill_value=0)
        .set_axis([ENROLLED_ACTIVE_COLUMN, NOT_ENROLLED_ACTIVE_COLUMN], axis=1)
        .reset_index()
        .rename_axis(columns=None)
    )


def situacion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    matriculados = cruce.loc[cruce[ENROLLED_COLUMN], CLAVES + [ENROLLMENT_STATE_COLUMN]]
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + [CONDITION_COLUMN]]
    res = matriculados.merge(condicion, on=CLAVES, how="left")
    res[SITUATION_COLUMN] = res[CONDITION_COLUMN].fillna(CONDITION_NOT_PRESENTED)
    res.loc[res[ENROLLMENT_STATE_COLUMN] == ENROLLMENT_STATE_DROPPED, SITUATION_COLUMN] = CONDITION_DROPPED
    return res[CLAVES + [SITUATION_COLUMN]].sort_values(CLAVES).reset_index(drop=True)


def resumen_situacion_academica(situacion: pd.DataFrame) -> pd.DataFrame:
    conteo = (
        situacion.groupby([SUBJECT_COLUMN, SITUATION_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=SITUACIONES, fill_value=0)
    )
    conteo.loc[SITUATION_GENERAL] = conteo.sum()
    res = conteo.stack().rename(STUDENTS_COLUMN).reset_index()
    res[PERCENTAGE_COLUMN] = (res[STUDENTS_COLUMN] / res.groupby(SUBJECT_COLUMN)[STUDENTS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return res
