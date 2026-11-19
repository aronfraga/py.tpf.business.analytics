from pathlib import Path
import sys
import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[2])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
import constants as const

try:
    from .kpis_calificaciones import condicion_por_estudiante
except ImportError:
    from kpis_calificaciones import condicion_por_estudiante


CLAVES = const.KEY_COLUMNS
SITUACIONES = const.SITUATIONS


def estudiantes_activos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    activos = participacion.loc[participacion[const.INTERACTIONS_COLUMN] > 0, CLAVES]
    res = activos.merge(cruce[CLAVES + [const.ENROLLED_COLUMN]], on=CLAVES, how="left")
    res[const.ENROLLED_COLUMN] = res[const.ENROLLED_COLUMN].fillna(False).astype(bool)
    return res.sort_values(CLAVES).reset_index(drop=True)

def resumen_activos_por_matricula(activos: pd.DataFrame) -> pd.DataFrame:
    return (
        activos.groupby([const.SUBJECT_COLUMN, const.ENROLLED_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=[True, False], fill_value=0)
        .set_axis([const.ENROLLED_ACTIVE_COLUMN, const.NOT_ENROLLED_ACTIVE_COLUMN], axis=1)
        .reset_index()
        .rename_axis(columns=None)
    )

def situacion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    matriculados = cruce.loc[cruce[const.ENROLLED_COLUMN], CLAVES + [const.ENROLLMENT_STATE_COLUMN]]
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + [const.CONDITION_COLUMN]]
    res = matriculados.merge(condicion, on=CLAVES, how="left")
    res[const.SITUATION_COLUMN] = res[const.CONDITION_COLUMN].fillna(const.CONDITION_NOT_PRESENTED)
    res.loc[res[const.ENROLLMENT_STATE_COLUMN] == const.ENROLLMENT_STATE_DROPPED, const.SITUATION_COLUMN] = const.CONDITION_DROPPED
    return res[CLAVES + [const.SITUATION_COLUMN]].sort_values(CLAVES).reset_index(drop=True)

def resumen_situacion_academica(situacion: pd.DataFrame) -> pd.DataFrame:
    conteo = (
        situacion.groupby([const.SUBJECT_COLUMN, const.SITUATION_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=SITUACIONES, fill_value=0)
    )
    conteo.loc[const.SITUATION_GENERAL] = conteo.sum()
    res = conteo.stack().rename(const.STUDENTS_COLUMN).reset_index()
    res[const.PERCENTAGE_COLUMN] = (res[const.STUDENTS_COLUMN] / res.groupby(const.SUBJECT_COLUMN)[const.STUDENTS_COLUMN].transform("sum") * const.PERCENT_FACTOR).round(const.ROUND_DECIMALS)
    return res
