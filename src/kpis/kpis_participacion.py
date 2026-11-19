"""KPIs de participación: sesiones, tiempo en la plataforma, cobertura y estudiantes activos.

Entrada : data/integrado/{trazabilidad,participacion,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).

Las funciones de KPI son puras (reciben y devuelven DataFrames).

La justificación y los controles de sensibilidad de cada KPI están en participacion.ipynb.
"""
import sys
from pathlib import Path

import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[1])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
from constants import (
    ACTIVE_COLUMN,
    ACTIVE_COUNT_COLUMN,
    ACTIVE_PERCENT_COLUMN,
    ACTIVITY_DAYS_LIMIT,
    AVERAGE_ACTIVE_COLUMN,
    AVERAGE_ENROLLED_COLUMN,
    AVERAGE_MINUTES_ACTIVE_COLUMN,
    AVERAGE_MINUTES_ENROLLED_COLUMN,
    COVERAGE_PERCENT_COLUMN,
    CUTOFF_DATE_COLUMN,
    ENROLLED_COLUMN,
    ENROLLED_COUNT_COLUMN,
    ESTIMATED_USAGE_MINUTES_COLUMN,
    EVENT_DATE_COLUMN,
    INACTIVE_COUNT_COLUMN,
    INACTIVE_PERCENT_COLUMN,
    INTERACTIONS_COLUMN,
    IS_ENROLLED_COLUMN,
    KEY_COLUMNS,
    LAST_INTERACTION_COLUMN,
    MEDIAN_ENROLLED_COLUMN,
    MEDIAN_MINUTES_ENROLLED_COLUMN,
    NEW_SESSION_COLUMN,
    NOT_ENROLLED_WITH_ACTIVITY_COLUMN,
    PARTICIPATES_COLUMN,
    PARTICIPATION_THRESHOLD,
    PERCENT_FACTOR,
    ROUND_DECIMALS,
    SECONDS_PER_DAY,
    SESSIONS_SOURCE_COLUMN,
    SESSION_GAP,
    SUBJECT_COLUMN,
    TIME_MINUTES_COLUMN,
    TOTAL_STUDENTS_COLUMN,
    USER_COLUMN,
    WITH_PARTICIPATION_COLUMN,
)


CLAVES = KEY_COLUMNS

# Una sesión termina cuando el estudiante pasa más de este tiempo sin generar eventos.
UMBRAL_SESION = SESSION_GAP
UMBRAL_PARTICIPACION = PARTICIPATION_THRESHOLD  # interacciones que hay que superar para contar como participante
DIAS_ACTIVIDAD = ACTIVITY_DAYS_LIMIT  # días máximos sin interacción para seguir considerándose activo


# ----------------------------------------------------------------------------
# Auxiliares
# ----------------------------------------------------------------------------
def _matriculados(cruce: pd.DataFrame) -> pd.DataFrame:
    return cruce.loc[cruce[ENROLLED_COLUMN], CLAVES]


def _universo_de_alumnos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Matriculados más los no matriculados con al menos una interacción, por asignatura.

    El reporte de participación lista a todo el padrón de la plataforma en cada aula, así que
    quien no está matriculado y nunca participó no se cuenta.
    """
    con_actividad = participacion.loc[participacion[INTERACTIONS_COLUMN] > 0, CLAVES]
    return pd.concat([_matriculados(cruce), con_actividad]).drop_duplicates()


# ----------------------------------------------------------------------------
# KPI 1: promedio de sesiones por estudiante
# ----------------------------------------------------------------------------
def sesiones_por_estudiante(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                            umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
    """Cantidad de sesiones de cada estudiante matriculado, por asignatura.

    El log de trazabilidad no trae un identificador de sesión, así que se reconstruye: una
    sesión es una secuencia de eventos de un usuario en una asignatura donde entre eventos
    consecutivos pasan como máximo `umbral`. Los matriculados sin actividad quedan con 0
    sesiones, para que no inflen el promedio quienes nunca ingresaron.

    Devuelve: materia, usuario, sesiones.
    """
    eventos = trazabilidad.sort_values(CLAVES + [EVENT_DATE_COLUMN])
    brecha = eventos.groupby(CLAVES)[EVENT_DATE_COLUMN].diff()
    # Un evento abre sesión nueva si es el primero del usuario (NaT) o si superó el umbral.
    eventos = eventos.assign(**{NEW_SESSION_COLUMN: brecha.isna() | (brecha > umbral)})
    sesiones = eventos.groupby(CLAVES)[NEW_SESSION_COLUMN].sum().astype(int).rename(SESSIONS_SOURCE_COLUMN)

    return (
        _matriculados(cruce).merge(sesiones.reset_index(), on=CLAVES, how="left")
        .fillna({SESSIONS_SOURCE_COLUMN: 0})
        .astype({SESSIONS_SOURCE_COLUMN: int})
    )


def sesiones_promedio_por_estudiante(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                                     umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
    """KPI: promedio de sesiones por estudiante, por asignatura.

    Devuelve una fila por asignatura: matriculados, activos, promedio_matriculados (incluye
    inactivos), promedio_activos (solo quienes tuvieron al menos una sesión) y
    mediana_matriculados (robusta a usos extremos).
    """
    por_estudiante = sesiones_por_estudiante(trazabilidad, cruce, umbral)
    activos = por_estudiante[por_estudiante[SESSIONS_SOURCE_COLUMN] > 0]
    return pd.DataFrame(
        {
            ENROLLED_COUNT_COLUMN: por_estudiante.groupby(SUBJECT_COLUMN)[USER_COLUMN].nunique(),
            ACTIVE_COUNT_COLUMN: activos.groupby(SUBJECT_COLUMN)[USER_COLUMN].nunique(),
            AVERAGE_ENROLLED_COLUMN: por_estudiante.groupby(SUBJECT_COLUMN)[SESSIONS_SOURCE_COLUMN].mean(),
            AVERAGE_ACTIVE_COLUMN: activos.groupby(SUBJECT_COLUMN)[SESSIONS_SOURCE_COLUMN].mean(),
            MEDIAN_ENROLLED_COLUMN: por_estudiante.groupby(SUBJECT_COLUMN)[SESSIONS_SOURCE_COLUMN].median(),
        }
    ).round(ROUND_DECIMALS).reset_index()


# ----------------------------------------------------------------------------
# KPI 2: tiempo promedio en la plataforma
# ----------------------------------------------------------------------------
def tiempo_por_estudiante(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Minutos de uso estimado de cada estudiante matriculado, por asignatura.

    El reporte de participación tiene una fila por estudiante y asignatura con el tiempo ya
    acumulado (`tiempo_estimado_de_uso_min`). Los matriculados que no figuran en el reporte
    quedan con 0 minutos.

    Devuelve: materia, usuario, tiempo_min.
    """
    tiempo = participacion[CLAVES + [ESTIMATED_USAGE_MINUTES_COLUMN]].rename(
        columns={ESTIMATED_USAGE_MINUTES_COLUMN: TIME_MINUTES_COLUMN}
    )
    return _matriculados(cruce).merge(tiempo, on=CLAVES, how="left").fillna({TIME_MINUTES_COLUMN: 0})


def tiempo_promedio_en_plataforma(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """KPI: tiempo promedio en la plataforma por estudiante, por asignatura (en minutos).

    Devuelve una fila por asignatura: matriculados, activos, promedio_min_matriculados,
    promedio_min_activos y mediana_min_matriculados. La distribución es asimétrica (pocos
    estudiantes con uso muy alto), por eso se incluye la mediana.
    """
    por_estudiante = tiempo_por_estudiante(participacion, cruce)
    activos = por_estudiante[por_estudiante[TIME_MINUTES_COLUMN] > 0]
    return pd.DataFrame(
        {
            ENROLLED_COUNT_COLUMN: por_estudiante.groupby(SUBJECT_COLUMN)[USER_COLUMN].nunique(),
            ACTIVE_COUNT_COLUMN: activos.groupby(SUBJECT_COLUMN)[USER_COLUMN].nunique(),
            AVERAGE_MINUTES_ENROLLED_COLUMN: por_estudiante.groupby(SUBJECT_COLUMN)[TIME_MINUTES_COLUMN].mean(),
            AVERAGE_MINUTES_ACTIVE_COLUMN: activos.groupby(SUBJECT_COLUMN)[TIME_MINUTES_COLUMN].mean(),
            MEDIAN_MINUTES_ENROLLED_COLUMN: por_estudiante.groupby(SUBJECT_COLUMN)[TIME_MINUTES_COLUMN].median(),
        }
    ).round(ROUND_DECIMALS).reset_index()


# ----------------------------------------------------------------------------
# KPI 3: cobertura de participación
# ----------------------------------------------------------------------------
def cobertura_participacion(participacion: pd.DataFrame, cruce: pd.DataFrame,
                            umbral: float = UMBRAL_PARTICIPACION,
                            columna: str = INTERACTIONS_COLUMN) -> pd.DataFrame:
    """KPI: porcentaje de cobertura de participación, por asignatura.

    Cobertura = alumnos con `columna` > `umbral` / total de alumnos * 100. El total es el
    universo de alumnos (matriculados y no matriculados con actividad) y no depende del
    umbral: solo el numerador cambia. Con umbral=0 mide quién participó al menos una vez.

    Parámetros:
      - umbral: valor que la participación debe superar (estricto).
      - columna: métrica a evaluar ("interacciones", "tiempo_estimado_de_uso_min", "avance", ...).

    Devuelve una fila por asignatura: total_alumnos, matriculados,
    no_matriculados_con_actividad, con_participacion, cobertura_pct.
    """
    universo = _universo_de_alumnos(participacion, cruce).merge(
        participacion[CLAVES + [columna]], on=CLAVES, how="left"
    ).fillna({columna: 0})
    universo[IS_ENROLLED_COLUMN] = universo.set_index(CLAVES).index.isin(_matriculados(cruce).set_index(CLAVES).index)
    universo[PARTICIPATES_COLUMN] = universo[columna] > umbral

    resumen = universo.groupby(SUBJECT_COLUMN).agg(
        **{TOTAL_STUDENTS_COLUMN: (USER_COLUMN, "nunique"), ENROLLED_COUNT_COLUMN: (IS_ENROLLED_COLUMN, "sum"), WITH_PARTICIPATION_COLUMN: (PARTICIPATES_COLUMN, "sum")},
    )
    resumen[NOT_ENROLLED_WITH_ACTIVITY_COLUMN] = resumen[TOTAL_STUDENTS_COLUMN] - resumen[ENROLLED_COUNT_COLUMN]
    resumen[COVERAGE_PERCENT_COLUMN] = (PERCENT_FACTOR * resumen[WITH_PARTICIPATION_COLUMN] / resumen[TOTAL_STUDENTS_COLUMN]).round(ROUND_DECIMALS)
    return resumen[
        [TOTAL_STUDENTS_COLUMN, ENROLLED_COUNT_COLUMN, NOT_ENROLLED_WITH_ACTIVITY_COLUMN, WITH_PARTICIPATION_COLUMN, COVERAGE_PERCENT_COLUMN]
    ].reset_index()


# ----------------------------------------------------------------------------
# KPI 4: estudiantes activos vs. inactivos
# ----------------------------------------------------------------------------
def estudiantes_activos_vs_inactivos(participacion: pd.DataFrame, cruce: pd.DataFrame,
                                     dias: int = DIAS_ACTIVIDAD,
                                     fecha_corte: pd.Timestamp | None = None) -> pd.DataFrame:
    """KPI: estudiantes activos vs. inactivos, por asignatura.

    Un estudiante es activo si su última interacción ocurrió dentro de los últimos `dias` días
    respecto de la fecha de corte; inactivo si pasaron más de `dias` días o si nunca interactuó.
    A diferencia de la cobertura (si participó alguna vez), mide el estado reciente.

    `fecha_corte` es, por defecto, la última interacción de todo el reporte (la fecha del corte
    de los datos), para que el resultado no dependa de cuándo se ejecute.

    Devuelve una fila por asignatura: total_alumnos, activos, inactivos, pct_activos,
    pct_inactivos, fecha_corte.
    """
    if fecha_corte is None:
        fecha_corte = participacion[LAST_INTERACTION_COLUMN].max()

    universo = _universo_de_alumnos(participacion, cruce).merge(
        participacion[CLAVES + [LAST_INTERACTION_COLUMN]], on=CLAVES, how="left"
    )
    dias_sin_interaccion = (fecha_corte - universo[LAST_INTERACTION_COLUMN]).dt.total_seconds() / SECONDS_PER_DAY
    # NaN (nunca interactuó) compara como False -> inactivo
    universo[ACTIVE_COLUMN] = dias_sin_interaccion <= dias

    resumen = universo.groupby(SUBJECT_COLUMN)[ACTIVE_COLUMN].agg(**{TOTAL_STUDENTS_COLUMN: "size", ACTIVE_COUNT_COLUMN: "sum"})
    resumen[INACTIVE_COUNT_COLUMN] = resumen[TOTAL_STUDENTS_COLUMN] - resumen[ACTIVE_COUNT_COLUMN]
    resumen[ACTIVE_PERCENT_COLUMN] = (PERCENT_FACTOR * resumen[ACTIVE_COUNT_COLUMN] / resumen[TOTAL_STUDENTS_COLUMN]).round(ROUND_DECIMALS)
    resumen[INACTIVE_PERCENT_COLUMN] = (PERCENT_FACTOR - resumen[ACTIVE_PERCENT_COLUMN]).round(ROUND_DECIMALS)
    resumen[CUTOFF_DATE_COLUMN] = fecha_corte.normalize()
    return resumen.reset_index()
