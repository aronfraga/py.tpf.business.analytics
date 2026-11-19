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

UMBRAL_SESION = SESSION_GAP
UMBRAL_PARTICIPACION = PARTICIPATION_THRESHOLD
DIAS_ACTIVIDAD = ACTIVITY_DAYS_LIMIT


def _matriculados(cruce: pd.DataFrame) -> pd.DataFrame:
    return cruce.loc[cruce[ENROLLED_COLUMN], CLAVES]


def _universo_de_alumnos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    con_actividad = participacion.loc[participacion[INTERACTIONS_COLUMN] > 0, CLAVES]
    return pd.concat([_matriculados(cruce), con_actividad]).drop_duplicates()


def sesiones_por_estudiante(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                            umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
    eventos = trazabilidad.sort_values(CLAVES + [EVENT_DATE_COLUMN])
    brecha = eventos.groupby(CLAVES)[EVENT_DATE_COLUMN].diff()
    eventos = eventos.assign(**{NEW_SESSION_COLUMN: brecha.isna() | (brecha > umbral)})
    sesiones = eventos.groupby(CLAVES)[NEW_SESSION_COLUMN].sum().astype(int).rename(SESSIONS_SOURCE_COLUMN)

    return (
        _matriculados(cruce).merge(sesiones.reset_index(), on=CLAVES, how="left")
        .fillna({SESSIONS_SOURCE_COLUMN: 0})
        .astype({SESSIONS_SOURCE_COLUMN: int})
    )


def sesiones_promedio_por_estudiante(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                                     umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
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


def tiempo_por_estudiante(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    tiempo = participacion[CLAVES + [ESTIMATED_USAGE_MINUTES_COLUMN]].rename(
        columns={ESTIMATED_USAGE_MINUTES_COLUMN: TIME_MINUTES_COLUMN}
    )
    return _matriculados(cruce).merge(tiempo, on=CLAVES, how="left").fillna({TIME_MINUTES_COLUMN: 0})


def tiempo_promedio_en_plataforma(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
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


def cobertura_participacion(participacion: pd.DataFrame, cruce: pd.DataFrame,
                            umbral: float = UMBRAL_PARTICIPACION,
                            columna: str = INTERACTIONS_COLUMN) -> pd.DataFrame:
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


def estudiantes_activos_vs_inactivos(participacion: pd.DataFrame, cruce: pd.DataFrame,
                                     dias: int = DIAS_ACTIVIDAD,
                                     fecha_corte: pd.Timestamp | None = None) -> pd.DataFrame:
    if fecha_corte is None:
        fecha_corte = participacion[LAST_INTERACTION_COLUMN].max()

    universo = _universo_de_alumnos(participacion, cruce).merge(
        participacion[CLAVES + [LAST_INTERACTION_COLUMN]], on=CLAVES, how="left"
    )
    dias_sin_interaccion = (fecha_corte - universo[LAST_INTERACTION_COLUMN]).dt.total_seconds() / SECONDS_PER_DAY
    universo[ACTIVE_COLUMN] = dias_sin_interaccion <= dias

    resumen = universo.groupby(SUBJECT_COLUMN)[ACTIVE_COLUMN].agg(**{TOTAL_STUDENTS_COLUMN: "size", ACTIVE_COUNT_COLUMN: "sum"})
    resumen[INACTIVE_COUNT_COLUMN] = resumen[TOTAL_STUDENTS_COLUMN] - resumen[ACTIVE_COUNT_COLUMN]
    resumen[ACTIVE_PERCENT_COLUMN] = (PERCENT_FACTOR * resumen[ACTIVE_COUNT_COLUMN] / resumen[TOTAL_STUDENTS_COLUMN]).round(ROUND_DECIMALS)
    resumen[INACTIVE_PERCENT_COLUMN] = (PERCENT_FACTOR - resumen[ACTIVE_PERCENT_COLUMN]).round(ROUND_DECIMALS)
    resumen[CUTOFF_DATE_COLUMN] = fecha_corte.normalize()
    return resumen.reset_index()
