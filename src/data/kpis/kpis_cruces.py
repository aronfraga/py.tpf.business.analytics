from pathlib import Path
from scipy import stats
import sys
import numpy as np
import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[2])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
import constants as const

try:
    from .kpis_calificaciones import CONDICIONES, condicion_por_estudiante, nota_por_estudiante
    from .kpis_participacion import tiempo_por_estudiante
    from .kpis_trazabilidad import cargar_trazabilidad, clasificar_interacciones, marcar_ingresos
except ImportError:
    from kpis_calificaciones import CONDICIONES, condicion_por_estudiante, nota_por_estudiante
    from kpis_participacion import tiempo_por_estudiante
    from kpis_trazabilidad import cargar_trazabilidad, clasificar_interacciones, marcar_ingresos


CLAVES = const.KEY_COLUMNS
GRUPOS = const.GROUPS
INDICADORES = const.INDICATORS


def participacion_vs_notas(
        participacion: pd.DataFrame, calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    tiempo = tiempo_por_estudiante(participacion, cruce)
    notas = nota_por_estudiante(calificaciones)[CLAVES + [const.GRADE_PERCENT_COLUMN]]
    res = tiempo.merge(notas, on=CLAVES, how="left")
    res[const.PRESENTED_COLUMN] = res[const.GRADE_PERCENT_COLUMN].notna()
    res[const.GRADE_PERCENT_COLUMN] = res[const.GRADE_PERCENT_COLUMN].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)

def correlacion_participacion_nota(tabla: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for materia, g in tabla.groupby(const.SUBJECT_COLUMN):
        pendiente = np.polyfit(g[const.TIME_MINUTES_COLUMN], g[const.GRADE_PERCENT_COLUMN], 1)[0] * const.MINUTES_PER_HOUR
        filas.append({
            const.SUBJECT_COLUMN: materia,
            const.STUDENTS_COLUMN: len(g),
            const.PEARSON_COLUMN: g[const.TIME_MINUTES_COLUMN].corr(g[const.GRADE_PERCENT_COLUMN]),
            const.SPEARMAN_COLUMN: g[const.TIME_MINUTES_COLUMN].rank().corr(g[const.GRADE_PERCENT_COLUMN].rank()),
            const.SLOPE_COLUMN: pendiente,
        })
    return pd.DataFrame(filas).round(const.CORRELATION_DECIMALS)

def linea_de_tendencia(tabla: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for materia, g in tabla.groupby(const.SUBJECT_COLUMN):
        pendiente, ordenada = np.polyfit(g[const.TIME_MINUTES_COLUMN], g[const.GRADE_PERCENT_COLUMN], 1)
        x0, x1 = g[const.TIME_MINUTES_COLUMN].min(), g[const.TIME_MINUTES_COLUMN].max()
        if pendiente > 0:
            x1 = min(x1, (const.GRADE_SCALE_MAX - ordenada) / pendiente)
        elif pendiente < 0:
            x1 = min(x1, (0 - ordenada) / pendiente)
        for x in (x0, x1):
            filas.append(
                {const.SUBJECT_COLUMN: materia, const.TIME_MINUTES_COLUMN: x, const.GRADE_PERCENT_COLUMN: pendiente * x + ordenada})
    return pd.DataFrame(filas).round(const.ROUND_DECIMALS)

def nota_por_tramo_de_participacion(tabla: pd.DataFrame, tramos: int = const.PARTICIPATION_BRACKET_COUNT) -> pd.DataFrame:
    piezas = []
    for materia, g in tabla.groupby(const.SUBJECT_COLUMN):
        tramo = pd.qcut(g[const.TIME_MINUTES_COLUMN], tramos, duplicates="drop")
        res = (
            g.groupby(tramo, observed=True)
            .agg(**{const.TIME_FROM_MINUTES_COLUMN: (const.TIME_MINUTES_COLUMN, "min"), const.TIME_TO_MINUTES_COLUMN: (const.TIME_MINUTES_COLUMN, "max"), const.STUDENTS_COLUMN: (const.USER_COLUMN, "size"), const.AVERAGE_GRADE_PERCENT_COLUMN: (const.GRADE_PERCENT_COLUMN, "mean")})
            .reset_index(drop=True)
        )
        res.insert(0, const.BRACKET_COLUMN, range(1, len(res) + 1))
        res.insert(0, const.SUBJECT_COLUMN, materia)
        piezas.append(res)
    return pd.concat(piezas, ignore_index=True).round(const.ROUND_DECIMALS)

def prueba_de_correlacion(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    datos = tabla[tabla[const.PRESENTED_COLUMN]] if solo_presentados else tabla
    filas = []
    for materia, g in datos.groupby(const.SUBJECT_COLUMN):
        pearson = stats.pearsonr(g[const.TIME_MINUTES_COLUMN], g[const.GRADE_PERCENT_COLUMN])
        ic = pearson.confidence_interval(const.CONFIDENCE_LEVEL)
        spearman = stats.spearmanr(g[const.TIME_MINUTES_COLUMN], g[const.GRADE_PERCENT_COLUMN])
        filas.append({
            const.SUBJECT_COLUMN: materia, const.STUDENTS_COLUMN: len(g),
            const.PEARSON_COLUMN: pearson.statistic, const.PEARSON_CI_LOW_COLUMN: ic.low, const.PEARSON_CI_HIGH_COLUMN: ic.high,
            const.PEARSON_P_COLUMN: pearson.pvalue,
            const.SPEARMAN_COLUMN: spearman.statistic, const.SPEARMAN_P_COLUMN: spearman.pvalue,
        })
    res = pd.DataFrame(filas)
    res[const.SIGNIFICANT_COLUMN] = (res[const.PEARSON_P_COLUMN] < const.SIGNIFICANCE_LEVEL) & (res[const.SPEARMAN_P_COLUMN] < const.SIGNIFICANCE_LEVEL)
    return res.round(const.CORRELATION_TEST_DECIMALS)

def tiempo_por_condicion(tabla: pd.DataFrame, calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + [const.CONDITION_COLUMN]]
    res = tabla.merge(condicion, on=CLAVES, how="left")
    res[const.CONDITION_COLUMN] = res[const.CONDITION_COLUMN].fillna(const.CONDITION_NOT_PRESENTED)
    return res

def resumen_tiempo_por_condicion(tabla_condicion: pd.DataFrame) -> pd.DataFrame:
    res = (
        tabla_condicion.groupby([const.SUBJECT_COLUMN, const.CONDITION_COLUMN])[const.TIME_MINUTES_COLUMN]
        .agg(**{const.STUDENTS_COLUMN: "size", const.AVERAGE_MINUTES_COLUMN: "mean", const.MEDIAN_MINUTES_COLUMN: "median"})
    )
    completo = pd.MultiIndex.from_product(
        [sorted(tabla_condicion[const.SUBJECT_COLUMN].unique()), GRUPOS], names=[const.SUBJECT_COLUMN, const.CONDITION_COLUMN])
    res = res.reindex(completo).reset_index()
    res[const.STUDENTS_COLUMN] = res[const.STUDENTS_COLUMN].fillna(0).astype(int)
    return res.round(1)

def indicadores_de_trazabilidad(
        trazabilidad: pd.DataFrame, cruce: pd.DataFrame, minutos_inactividad: int = const.INACTIVITY_MINUTES) -> pd.DataFrame:
    eventos = marcar_ingresos(trazabilidad, minutos_inactividad)
    tipo = clasificar_interacciones(eventos)
    eventos = eventos.assign(
        **{const.WEEK_SOURCE_COLUMN: eventos[const.EVENT_DATE_COLUMN].dt.to_period(const.WEEKLY_FREQUENCY), const.IS_MATERIAL_COLUMN: tipo == const.TYPE_STUDY_MATERIAL, const.IS_FORUM_COLUMN: tipo == const.TYPE_FORUMS},
    )
    indicadores = eventos.groupby(CLAVES).agg(
        **{const.ACTIVE_DAYS_COLUMN: (const.DAY_COLUMN, "nunique"), const.ENTRIES_COLUMN: (const.ENTRY_COLUMN, "sum"), const.ACTIVE_WEEKS_COLUMN: (const.WEEK_SOURCE_COLUMN, "nunique"), const.MATERIAL_INTERACTIONS_COLUMN: (const.IS_MATERIAL_COLUMN, "sum"), const.FORUM_INTERACTIONS_COLUMN: (const.IS_FORUM_COLUMN, "sum")},
    ).reset_index()

    matriculados = cruce.loc[cruce[const.ENROLLED_COLUMN], CLAVES]
    res = matriculados.merge(indicadores, on=CLAVES, how="left").fillna(0)
    res[INDICADORES] = res[INDICADORES].astype(int)
    return res

def trazabilidad_vs_notas(
        trazabilidad: pd.DataFrame, calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    notas = nota_por_estudiante(calificaciones)[CLAVES + [const.GRADE_PERCENT_COLUMN]]
    res = indicadores_de_trazabilidad(trazabilidad, cruce).merge(notas, on=CLAVES, how="left")
    res[const.PRESENTED_COLUMN] = res[const.GRADE_PERCENT_COLUMN].notna()
    res[const.GRADE_PERCENT_COLUMN] = res[const.GRADE_PERCENT_COLUMN].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)

def correlaciones_trazabilidad_nota(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    datos = tabla[tabla[const.PRESENTED_COLUMN]] if solo_presentados else tabla
    filas = []
    for materia, g in datos.groupby(const.SUBJECT_COLUMN):
        for indicador in INDICADORES:
            r = stats.spearmanr(g[indicador], g[const.GRADE_PERCENT_COLUMN])
            filas.append({const.SUBJECT_COLUMN: materia, const.INDICATOR_COLUMN: indicador, const.STUDENTS_COLUMN: len(
                g),
                          const.SPEARMAN_COLUMN: r.statistic, const.P_VALUE_COLUMN: r.pvalue})
    res = pd.DataFrame(filas)
    res[const.SIGNIFICANT_COLUMN] = res[const.P_VALUE_COLUMN] < const.SIGNIFICANCE_LEVEL
    return res.round({const.SPEARMAN_COLUMN: const.SPEARMAN_DECIMALS, const.P_VALUE_COLUMN: const.P_VALUE_DECIMALS})

def matriz_correlaciones(correlaciones: pd.DataFrame) -> pd.DataFrame:
    return correlaciones.pivot(index=const.INDICATOR_COLUMN, columns=const.SUBJECT_COLUMN, values=const.SPEARMAN_COLUMN).reindex(
        INDICADORES)

def indicador_mas_relacionado(correlaciones: pd.DataFrame) -> str:
    return correlaciones.assign(**{const.ABSOLUTE_R_COLUMN: correlaciones[const.SPEARMAN_COLUMN].abs()}).groupby(const.INDICATOR_COLUMN)[const.ABSOLUTE_R_COLUMN].mean().idxmax()
