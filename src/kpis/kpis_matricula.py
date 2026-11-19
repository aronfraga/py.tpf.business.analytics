"""KPIs de matrícula: estudiantes activos según su matrícula y situación académica.

Entrada : data/integrado/{participacion,calificaciones,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).

Para calcular todo de una vez:
    from kpis_matricula import calcular_kpis_matricula
    kpis = calcular_kpis_matricula()
    kpis["activos_por_matricula"]   # DataFrame

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
    DATA_PATH,
    ENROLLED_ACTIVE_COLUMN,
    ENROLLED_COLUMN,
    ENROLLMENT_CROSS_FILE,
    ENROLLMENT_STATE_COLUMN,
    ENROLLMENT_STATE_DROPPED,
    GRADES_FILE,
    INTEGRATED_FOLDER_NAME,
    INTERACTIONS_COLUMN,
    KEY_COLUMNS,
    KPI_ACADEMIC_SITUATION,
    KPI_ACADEMIC_SITUATION_SUMMARY,
    KPI_ACTIVE_BY_ENROLLMENT,
    KPI_ACTIVE_STUDENTS,
    NOT_ENROLLED_ACTIVE_COLUMN,
    PARTICIPATION_FILE,
    PERCENTAGE_COLUMN,
    PERCENT_FACTOR,
    ROUND_DECIMALS,
    SITUATIONS,
    SITUATION_COLORS,
    SITUATION_COLUMN,
    SITUATION_GENERAL,
    STATIC_FIGURE_DPI,
    STATIC_MIN_LABEL_PERCENT,
    STATIC_PERCENT_LABEL_TEMPLATE,
    STATIC_SITUATION_PERCENT_LABEL,
    STATIC_SITUATION_TITLE,
    STUDENTS_COLUMN,
    SUBJECT_COLUMN,
)

try:  # como paquete (kpis.kpis_matricula) o como módulo suelto (kpis_matricula)
    from .kpis_calificaciones import condicion_por_estudiante
except ImportError:
    from kpis_calificaciones import condicion_por_estudiante

# src/kpis/kpis_matricula.py -> raíz del proyecto -> data/
DATOS_POR_DEFECTO = DATA_PATH

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


def graficar_situacion_academica(resumen: pd.DataFrame, ruta: Path | None = None):
    """Barras horizontales apiladas (100 %) de la situación académica, por asignatura y en general.

    Usa matplotlib, que se importa acá para que el resto del módulo no lo requiera. Si se indica
    `ruta`, guarda la imagen. Devuelve la figura.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    colores = SITUATION_COLORS
    porcentajes = resumen.pivot(index=SUBJECT_COLUMN, columns=SITUATION_COLUMN, values=PERCENTAGE_COLUMN)[SITUACIONES]
    orden = [m for m in porcentajes.index if m != SITUATION_GENERAL] + [SITUATION_GENERAL]
    porcentajes = porcentajes.loc[orden]
    etiquetas = [m.capitalize() for m in porcentajes.index]

    fig, eje = plt.subplots(figsize=(9, 3.6))
    izquierda = np.zeros(len(porcentajes))
    for situacion in SITUACIONES:
        valores = porcentajes[situacion].to_numpy()
        barras = eje.barh(etiquetas, valores, left=izquierda, color=colores[situacion], label=situacion)
        eje.bar_label(barras, labels=[STATIC_PERCENT_LABEL_TEMPLATE.format(value=v) if v >= STATIC_MIN_LABEL_PERCENT else "" for v in valores], label_type="center",
                      fontsize=9, color="white")
        izquierda += valores
    eje.invert_yaxis()
    eje.set_xlim(0, 100)
    eje.set_xlabel(STATIC_SITUATION_PERCENT_LABEL)
    eje.set_title(STATIC_SITUATION_TITLE, loc="left")
    eje.spines[["top", "right"]].set_visible(False)
    eje.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=len(SITUACIONES), frameon=False)
    fig.tight_layout()
    if ruta is not None:
        fig.savefig(ruta, dpi=STATIC_FIGURE_DPI, bbox_inches="tight")
    return fig


# ----------------------------------------------------------------------------
# Todos los KPI
# ----------------------------------------------------------------------------
def calcular_kpis_matricula(datos=None) -> dict[str, pd.DataFrame]:
    """Lee los datos integrados y devuelve los KPI de matrícula como DataFrames.

    Claves: estudiantes_activos (detalle; los no matriculados son la alerta), activos_por_matricula,
    situacion_academica (detalle) y situacion_academica_resumen.
    """
    integrado = (Path(datos) if datos else DATOS_POR_DEFECTO) / INTEGRATED_FOLDER_NAME
    participacion = pd.read_parquet(integrado / PARTICIPATION_FILE)
    calificaciones = pd.read_parquet(integrado / GRADES_FILE)
    cruce = pd.read_parquet(integrado / ENROLLMENT_CROSS_FILE)

    activos = estudiantes_activos(participacion, cruce)
    situacion = situacion_academica(calificaciones, cruce)
    return {
        KPI_ACTIVE_STUDENTS: activos,
        KPI_ACTIVE_BY_ENROLLMENT: resumen_activos_por_matricula(activos),
        KPI_ACADEMIC_SITUATION: situacion,
        KPI_ACADEMIC_SITUATION_SUMMARY: resumen_situacion_academica(situacion),
    }
