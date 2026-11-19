from pathlib import Path
import sys
import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[2])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
import constants as const


CLAVES = const.KEY_COLUMNS

UMBRAL_SESION = const.SESSION_GAP
UMBRAL_PARTICIPACION = const.PARTICIPATION_THRESHOLD
DIAS_ACTIVIDAD = const.ACTIVITY_DAYS_LIMIT


def _matriculados(cruce: pd.DataFrame) -> pd.DataFrame:
    return cruce.loc[cruce[const.ENROLLED_COLUMN], CLAVES]

def _universo_de_alumnos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    con_actividad = participacion.loc[participacion[const.INTERACTIONS_COLUMN] > 0, CLAVES]
    return pd.concat([_matriculados(cruce), con_actividad]).drop_duplicates()

def sesiones_por_estudiante(
        trazabilidad: pd.DataFrame, cruce: pd.DataFrame, umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
    eventos = trazabilidad.sort_values(CLAVES + [const.EVENT_DATE_COLUMN])
    brecha = eventos.groupby(CLAVES)[const.EVENT_DATE_COLUMN].diff()
    eventos = eventos.assign(**{const.NEW_SESSION_COLUMN: brecha.isna() | (brecha > umbral)})
    sesiones = eventos.groupby(CLAVES)[const.NEW_SESSION_COLUMN].sum().astype(int).rename(const.SESSIONS_SOURCE_COLUMN)

    return (
        _matriculados(cruce).merge(sesiones.reset_index(), on=CLAVES, how="left")
        .fillna({const.SESSIONS_SOURCE_COLUMN: 0})
        .astype({const.SESSIONS_SOURCE_COLUMN: int})
    )

def sesiones_promedio_por_estudiante(
        trazabilidad: pd.DataFrame, cruce: pd.DataFrame, umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
    por_estudiante = sesiones_por_estudiante(trazabilidad, cruce, umbral)
    activos = por_estudiante[por_estudiante[const.SESSIONS_SOURCE_COLUMN] > 0]
    return pd.DataFrame(
        {
            const.ENROLLED_COUNT_COLUMN: por_estudiante.groupby(const.SUBJECT_COLUMN)[const.USER_COLUMN].nunique(),
            const.ACTIVE_COUNT_COLUMN: activos.groupby(const.SUBJECT_COLUMN)[const.USER_COLUMN].nunique(),
            const.AVERAGE_ENROLLED_COLUMN: por_estudiante.groupby(const.SUBJECT_COLUMN)[const.SESSIONS_SOURCE_COLUMN].mean(),
            const.AVERAGE_ACTIVE_COLUMN: activos.groupby(const.SUBJECT_COLUMN)[const.SESSIONS_SOURCE_COLUMN].mean(),
            const.MEDIAN_ENROLLED_COLUMN: por_estudiante.groupby(const.SUBJECT_COLUMN)[const.SESSIONS_SOURCE_COLUMN].median(),
        }
    ).round(const.ROUND_DECIMALS).reset_index()

def tiempo_por_estudiante(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    tiempo = participacion[CLAVES + [const.ESTIMATED_USAGE_MINUTES_COLUMN]].rename(
        columns={const.ESTIMATED_USAGE_MINUTES_COLUMN: const.TIME_MINUTES_COLUMN})
    return _matriculados(cruce).merge(tiempo, on=CLAVES, how="left").fillna({const.TIME_MINUTES_COLUMN: 0})

def tiempo_promedio_en_plataforma(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    por_estudiante = tiempo_por_estudiante(participacion, cruce)
    activos = por_estudiante[por_estudiante[const.TIME_MINUTES_COLUMN] > 0]
    return pd.DataFrame(
        {
            const.ENROLLED_COUNT_COLUMN: por_estudiante.groupby(const.SUBJECT_COLUMN)[const.USER_COLUMN].nunique(),
            const.ACTIVE_COUNT_COLUMN: activos.groupby(const.SUBJECT_COLUMN)[const.USER_COLUMN].nunique(),
            const.AVERAGE_MINUTES_ENROLLED_COLUMN: por_estudiante.groupby(const.SUBJECT_COLUMN)[const.TIME_MINUTES_COLUMN].mean(),
            const.AVERAGE_MINUTES_ACTIVE_COLUMN: activos.groupby(const.SUBJECT_COLUMN)[const.TIME_MINUTES_COLUMN].mean(),
            const.MEDIAN_MINUTES_ENROLLED_COLUMN: por_estudiante.groupby(const.SUBJECT_COLUMN)[const.TIME_MINUTES_COLUMN].median(),
        }
    ).round(const.ROUND_DECIMALS).reset_index()

def cobertura_participacion(participacion: pd.DataFrame, cruce: pd.DataFrame,
                            umbral: float = UMBRAL_PARTICIPACION,
                            columna: str = const.INTERACTIONS_COLUMN) -> pd.DataFrame:
    universo = _universo_de_alumnos(participacion, cruce).merge(
        participacion[CLAVES + [columna]], on=CLAVES, how="left").fillna({columna: 0})
    universo[const.IS_ENROLLED_COLUMN] = universo.set_index(CLAVES).index.isin(
        _matriculados(cruce).set_index(CLAVES).index)
    universo[const.PARTICIPATES_COLUMN] = universo[columna] > umbral

    resumen = universo.groupby(const.SUBJECT_COLUMN).agg(
        **{const.TOTAL_STUDENTS_COLUMN: (const.USER_COLUMN, "nunique"), const.ENROLLED_COUNT_COLUMN: (const.IS_ENROLLED_COLUMN, "sum"), const.WITH_PARTICIPATION_COLUMN: (const.PARTICIPATES_COLUMN, "sum")},
    )
    resumen[const.NOT_ENROLLED_WITH_ACTIVITY_COLUMN] = resumen[const.TOTAL_STUDENTS_COLUMN] - resumen[const.ENROLLED_COUNT_COLUMN]
    resumen[const.COVERAGE_PERCENT_COLUMN] = (const.PERCENT_FACTOR * resumen[const.WITH_PARTICIPATION_COLUMN] / resumen[const.TOTAL_STUDENTS_COLUMN]).round(const.ROUND_DECIMALS)
    return resumen[
        [const.TOTAL_STUDENTS_COLUMN, const.ENROLLED_COUNT_COLUMN, const.NOT_ENROLLED_WITH_ACTIVITY_COLUMN, const.WITH_PARTICIPATION_COLUMN, const.COVERAGE_PERCENT_COLUMN]
    ].reset_index()

def estudiantes_activos_vs_inactivos(participacion: pd.DataFrame, cruce: pd.DataFrame,
                                     dias: int = DIAS_ACTIVIDAD,
                                     fecha_corte: pd.Timestamp | None = None) -> pd.DataFrame:
    if fecha_corte is None:
        fecha_corte = participacion[const.LAST_INTERACTION_COLUMN].max()

    universo = _universo_de_alumnos(participacion, cruce).merge(
        participacion[CLAVES + [const.LAST_INTERACTION_COLUMN]], on=CLAVES, how="left")
    dias_sin_interaccion = (fecha_corte - universo[const.LAST_INTERACTION_COLUMN]).dt.total_seconds() / const.SECONDS_PER_DAY
    universo[const.ACTIVE_COLUMN] = dias_sin_interaccion <= dias

    resumen = universo.groupby(const.SUBJECT_COLUMN)[const.ACTIVE_COLUMN].agg(
        **{const.TOTAL_STUDENTS_COLUMN: "size", const.ACTIVE_COUNT_COLUMN: "sum"})
    resumen[const.INACTIVE_COUNT_COLUMN] = resumen[const.TOTAL_STUDENTS_COLUMN] - resumen[const.ACTIVE_COUNT_COLUMN]
    resumen[const.ACTIVE_PERCENT_COLUMN] = (const.PERCENT_FACTOR * resumen[const.ACTIVE_COUNT_COLUMN] / resumen[const.TOTAL_STUDENTS_COLUMN]).round(const.ROUND_DECIMALS)
    resumen[const.INACTIVE_PERCENT_COLUMN] = (const.PERCENT_FACTOR - resumen[const.ACTIVE_PERCENT_COLUMN]).round(
        const.ROUND_DECIMALS)
    resumen[const.CUTOFF_DATE_COLUMN] = fecha_corte.normalize()
    return resumen.reset_index()
