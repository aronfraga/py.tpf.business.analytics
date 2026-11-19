"""KPIs de matrícula: estudiantes activos según su matrícula y situación académica.

Entrada : data/integrado/{participacion,calificaciones,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).

Definiciones:
  - Activo      : tuvo al menos una interacción en el aula (`interacciones > 0` en el reporte de
                  participación). Estar listado en el reporte no alcanza: incluye a todo el padrón de la
                  plataforma en cada aula, incluso a quienes nunca entraron.
  - Matriculado : figura en el listado oficial de matriculados de esa asignatura (`matriculado` del cruce).
  - Situación   : baja, no se presentó, o la condición (promocionado, regular, libre) según la nota. Es el
                  desempeño actual, no una proyección de la condición final.

La justificación y los controles de cada KPI están en matricula.ipynb.
"""
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

try:  # como paquete (kpis.kpis_matricula) o como módulo suelto (kpis_matricula)
    from .kpis_calificaciones import condicion_por_estudiante
except ImportError:
    from kpis_calificaciones import condicion_por_estudiante


CLAVES = KEY_COLUMNS
SITUACIONES = SITUATIONS


# ----------------------------------------------------------------------------
# KPI 1: estudiantes activos matriculados y no matriculados (alerta de no inscriptos pero activos)
# ----------------------------------------------------------------------------
def estudiantes_activos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Estudiantes activos de cada asignatura y si están matriculados.

    Los no matriculados activos son la alerta: usan el aula sin estar inscriptos.

    Devuelve una fila por estudiante activo y asignatura: materia, usuario, matriculado.
    """
    activos = participacion.loc[participacion[INTERACTIONS_COLUMN] > 0, CLAVES]
    res = activos.merge(cruce[CLAVES + [ENROLLED_COLUMN]], on=CLAVES, how="left")
    res[ENROLLED_COLUMN] = res[ENROLLED_COLUMN].fillna(False).astype(bool)
    return res.sort_values(CLAVES).reset_index(drop=True)


def resumen_activos_por_matricula(activos: pd.DataFrame) -> pd.DataFrame:
    """KPI: cantidad de estudiantes activos matriculados y no matriculados, por asignatura.

    Devuelve una fila por asignatura: materia, matriculados_activos, no_matriculados_activos.
    """
    return (
        activos.groupby([SUBJECT_COLUMN, ENROLLED_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=[True, False], fill_value=0)
        .set_axis([ENROLLED_ACTIVE_COLUMN, NOT_ENROLLED_ACTIVE_COLUMN], axis=1)
        .reset_index()
        .rename_axis(columns=None)
    )


# ----------------------------------------------------------------------------
# KPI 2: situación académica general y por asignatura
# ----------------------------------------------------------------------------
def situacion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Situación académica de cada estudiante matriculado, por asignatura.

    Situaciones (ver SITUACIONES):
      - baja: la inscripción figura con estado Baja; tiene prioridad sobre las demás.
      - no se presentó: matriculado que no rindió ningún instrumento.
      - promocionado, regular, libre: condición según la nota (porcentaje de los puntos rendidos) y los
        umbrales de la asignatura definidos en kpis_calificaciones.py.

    Devuelve una fila por estudiante y asignatura: materia, usuario, situacion.
    """
    matriculados = cruce.loc[cruce[ENROLLED_COLUMN], CLAVES + [ENROLLMENT_STATE_COLUMN]]
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + [CONDITION_COLUMN]]
    res = matriculados.merge(condicion, on=CLAVES, how="left")
    res[SITUATION_COLUMN] = res[CONDITION_COLUMN].fillna(CONDITION_NOT_PRESENTED)
    res.loc[res[ENROLLMENT_STATE_COLUMN] == ENROLLMENT_STATE_DROPPED, SITUATION_COLUMN] = CONDITION_DROPPED
    return res[CLAVES + [SITUATION_COLUMN]].sort_values(CLAVES).reset_index(drop=True)


def resumen_situacion_academica(situacion: pd.DataFrame) -> pd.DataFrame:
    """KPI: cantidad y porcentaje de estudiantes por situación académica, por asignatura y en general.

    Devuelve (una fila por asignatura y situación, incluyendo las situaciones sin estudiantes, y una
    asignatura "general" con el total de todos los pares estudiante-asignatura): materia, situacion,
    estudiantes, porcentaje. Sirve directo para el gráfico de dona o de barras de Streamlit.
    """
    conteo = (
        situacion.groupby([SUBJECT_COLUMN, SITUATION_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=SITUACIONES, fill_value=0)
    )
    conteo.loc[SITUATION_GENERAL] = conteo.sum()
    res = conteo.stack().rename(STUDENTS_COLUMN).reset_index()
    res[PERCENTAGE_COLUMN] = (res[STUDENTS_COLUMN] / res.groupby(SUBJECT_COLUMN)[STUDENTS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return res
