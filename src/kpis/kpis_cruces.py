import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
_SRC_PATH = str(Path(__file__).resolve().parents[1])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
from constants import (
    ABSOLUTE_R_COLUMN,
    ACTIVE_DAYS_COLUMN,
    ACTIVE_WEEKS_COLUMN,
    AVERAGE_GRADE_PERCENT_COLUMN,
    AVERAGE_MINUTES_COLUMN,
    BRACKET_COLUMN,
    CONDITION_COLUMN,
    CONDITION_NOT_PRESENTED,
    CONFIDENCE_LEVEL,
    CORRELATION_DECIMALS,
    CORRELATION_TEST_DECIMALS,
    DAY_COLUMN,
    ENROLLED_COLUMN,
    ENTRIES_COLUMN,
    ENTRY_COLUMN,
    EVENT_DATE_COLUMN,
    FORUM_INTERACTIONS_COLUMN,
    GRADE_PERCENT_COLUMN,
    GRADE_SCALE_MAX,
    GROUPS,
    INACTIVITY_MINUTES,
    INDICATORS,
    INDICATOR_COLUMN,
    IS_FORUM_COLUMN,
    IS_MATERIAL_COLUMN,
    KEY_COLUMNS,
    MATERIAL_INTERACTIONS_COLUMN,
    MEDIAN_MINUTES_COLUMN,
    MINUTES_PER_HOUR,
    PARTICIPATION_BRACKET_COUNT,
    PEARSON_CI_HIGH_COLUMN,
    PEARSON_CI_LOW_COLUMN,
    PEARSON_COLUMN,
    PEARSON_P_COLUMN,
    PRESENTED_COLUMN,
    P_VALUE_COLUMN,
    P_VALUE_DECIMALS,
    ROUND_DECIMALS,
    SIGNIFICANCE_LEVEL,
    SIGNIFICANT_COLUMN,
    SLOPE_COLUMN,
    SPEARMAN_COLUMN,
    SPEARMAN_DECIMALS,
    SPEARMAN_P_COLUMN,
    STUDENTS_COLUMN,
    SUBJECT_COLUMN,
    TIME_FROM_MINUTES_COLUMN,
    TIME_MINUTES_COLUMN,
    TIME_TO_MINUTES_COLUMN,
    TYPE_FORUMS,
    TYPE_STUDY_MATERIAL,
    USER_COLUMN,
    WEEKLY_FREQUENCY,
    WEEK_SOURCE_COLUMN,
)

try:
    from .kpis_calificaciones import CONDICIONES, condicion_por_estudiante, nota_por_estudiante
    from .kpis_participacion import tiempo_por_estudiante
    from .kpis_trazabilidad import cargar_trazabilidad, clasificar_interacciones, marcar_ingresos
except ImportError:
    from kpis_calificaciones import CONDICIONES, condicion_por_estudiante, nota_por_estudiante
    from kpis_participacion import tiempo_por_estudiante
    from kpis_trazabilidad import cargar_trazabilidad, clasificar_interacciones, marcar_ingresos


CLAVES = KEY_COLUMNS
GRUPOS = GROUPS
INDICADORES = INDICATORS


def participacion_vs_notas(participacion: pd.DataFrame, calificaciones: pd.DataFrame,
                           cruce: pd.DataFrame) -> pd.DataFrame:
    tiempo = tiempo_por_estudiante(participacion, cruce)
    notas = nota_por_estudiante(calificaciones)[CLAVES + [GRADE_PERCENT_COLUMN]]
    res = tiempo.merge(notas, on=CLAVES, how="left")
    res[PRESENTED_COLUMN] = res[GRADE_PERCENT_COLUMN].notna()
    res[GRADE_PERCENT_COLUMN] = res[GRADE_PERCENT_COLUMN].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)


def correlacion_participacion_nota(tabla: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for materia, g in tabla.groupby(SUBJECT_COLUMN):
        pendiente = np.polyfit(g[TIME_MINUTES_COLUMN], g[GRADE_PERCENT_COLUMN], 1)[0] * MINUTES_PER_HOUR
        filas.append({
            SUBJECT_COLUMN: materia,
            STUDENTS_COLUMN: len(g),
            PEARSON_COLUMN: g[TIME_MINUTES_COLUMN].corr(g[GRADE_PERCENT_COLUMN]),
            SPEARMAN_COLUMN: g[TIME_MINUTES_COLUMN].rank().corr(g[GRADE_PERCENT_COLUMN].rank()),
            SLOPE_COLUMN: pendiente,
        })
    return pd.DataFrame(filas).round(CORRELATION_DECIMALS)


def linea_de_tendencia(tabla: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for materia, g in tabla.groupby(SUBJECT_COLUMN):
        pendiente, ordenada = np.polyfit(g[TIME_MINUTES_COLUMN], g[GRADE_PERCENT_COLUMN], 1)
        x0, x1 = g[TIME_MINUTES_COLUMN].min(), g[TIME_MINUTES_COLUMN].max()
        if pendiente > 0:
            x1 = min(x1, (GRADE_SCALE_MAX - ordenada) / pendiente)
        elif pendiente < 0:
            x1 = min(x1, (0 - ordenada) / pendiente)
        for x in (x0, x1):
            filas.append({SUBJECT_COLUMN: materia, TIME_MINUTES_COLUMN: x, GRADE_PERCENT_COLUMN: pendiente * x + ordenada})
    return pd.DataFrame(filas).round(ROUND_DECIMALS)


def nota_por_tramo_de_participacion(tabla: pd.DataFrame, tramos: int = PARTICIPATION_BRACKET_COUNT) -> pd.DataFrame:
    piezas = []
    for materia, g in tabla.groupby(SUBJECT_COLUMN):
        tramo = pd.qcut(g[TIME_MINUTES_COLUMN], tramos, duplicates="drop")
        res = (
            g.groupby(tramo, observed=True)
            .agg(**{TIME_FROM_MINUTES_COLUMN: (TIME_MINUTES_COLUMN, "min"), TIME_TO_MINUTES_COLUMN: (TIME_MINUTES_COLUMN, "max"), STUDENTS_COLUMN: (USER_COLUMN, "size"), AVERAGE_GRADE_PERCENT_COLUMN: (GRADE_PERCENT_COLUMN, "mean")})
            .reset_index(drop=True)
        )
        res.insert(0, BRACKET_COLUMN, range(1, len(res) + 1))
        res.insert(0, SUBJECT_COLUMN, materia)
        piezas.append(res)
    return pd.concat(piezas, ignore_index=True).round(ROUND_DECIMALS)


def prueba_de_correlacion(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    datos = tabla[tabla[PRESENTED_COLUMN]] if solo_presentados else tabla
    filas = []
    for materia, g in datos.groupby(SUBJECT_COLUMN):
        pearson = stats.pearsonr(g[TIME_MINUTES_COLUMN], g[GRADE_PERCENT_COLUMN])
        ic = pearson.confidence_interval(CONFIDENCE_LEVEL)
        spearman = stats.spearmanr(g[TIME_MINUTES_COLUMN], g[GRADE_PERCENT_COLUMN])
        filas.append({
            SUBJECT_COLUMN: materia, STUDENTS_COLUMN: len(g),
            PEARSON_COLUMN: pearson.statistic, PEARSON_CI_LOW_COLUMN: ic.low, PEARSON_CI_HIGH_COLUMN: ic.high,
            PEARSON_P_COLUMN: pearson.pvalue,
            SPEARMAN_COLUMN: spearman.statistic, SPEARMAN_P_COLUMN: spearman.pvalue,
        })
    res = pd.DataFrame(filas)
    res[SIGNIFICANT_COLUMN] = (res[PEARSON_P_COLUMN] < SIGNIFICANCE_LEVEL) & (res[SPEARMAN_P_COLUMN] < SIGNIFICANCE_LEVEL)
    return res.round(CORRELATION_TEST_DECIMALS)


def tiempo_por_condicion(tabla: pd.DataFrame, calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + [CONDITION_COLUMN]]
    res = tabla.merge(condicion, on=CLAVES, how="left")
    res[CONDITION_COLUMN] = res[CONDITION_COLUMN].fillna(CONDITION_NOT_PRESENTED)
    return res


def resumen_tiempo_por_condicion(tabla_condicion: pd.DataFrame) -> pd.DataFrame:
    res = (
        tabla_condicion.groupby([SUBJECT_COLUMN, CONDITION_COLUMN])[TIME_MINUTES_COLUMN]
        .agg(**{STUDENTS_COLUMN: "size", AVERAGE_MINUTES_COLUMN: "mean", MEDIAN_MINUTES_COLUMN: "median"})
    )
    completo = pd.MultiIndex.from_product([sorted(tabla_condicion[SUBJECT_COLUMN].unique()), GRUPOS], names=[SUBJECT_COLUMN, CONDITION_COLUMN])
    res = res.reindex(completo).reset_index()
    res[STUDENTS_COLUMN] = res[STUDENTS_COLUMN].fillna(0).astype(int)
    return res.round(1)


def indicadores_de_trazabilidad(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                                minutos_inactividad: int = INACTIVITY_MINUTES) -> pd.DataFrame:
    eventos = marcar_ingresos(trazabilidad, minutos_inactividad)
    tipo = clasificar_interacciones(eventos)
    eventos = eventos.assign(
        **{WEEK_SOURCE_COLUMN: eventos[EVENT_DATE_COLUMN].dt.to_period(WEEKLY_FREQUENCY), IS_MATERIAL_COLUMN: tipo == TYPE_STUDY_MATERIAL, IS_FORUM_COLUMN: tipo == TYPE_FORUMS},
    )
    indicadores = eventos.groupby(CLAVES).agg(
        **{ACTIVE_DAYS_COLUMN: (DAY_COLUMN, "nunique"), ENTRIES_COLUMN: (ENTRY_COLUMN, "sum"), ACTIVE_WEEKS_COLUMN: (WEEK_SOURCE_COLUMN, "nunique"), MATERIAL_INTERACTIONS_COLUMN: (IS_MATERIAL_COLUMN, "sum"), FORUM_INTERACTIONS_COLUMN: (IS_FORUM_COLUMN, "sum")},
    ).reset_index()

    matriculados = cruce.loc[cruce[ENROLLED_COLUMN], CLAVES]
    res = matriculados.merge(indicadores, on=CLAVES, how="left").fillna(0)
    res[INDICADORES] = res[INDICADORES].astype(int)
    return res


def trazabilidad_vs_notas(trazabilidad: pd.DataFrame, calificaciones: pd.DataFrame,
                          cruce: pd.DataFrame) -> pd.DataFrame:
    notas = nota_por_estudiante(calificaciones)[CLAVES + [GRADE_PERCENT_COLUMN]]
    res = indicadores_de_trazabilidad(trazabilidad, cruce).merge(notas, on=CLAVES, how="left")
    res[PRESENTED_COLUMN] = res[GRADE_PERCENT_COLUMN].notna()
    res[GRADE_PERCENT_COLUMN] = res[GRADE_PERCENT_COLUMN].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)


def correlaciones_trazabilidad_nota(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    datos = tabla[tabla[PRESENTED_COLUMN]] if solo_presentados else tabla
    filas = []
    for materia, g in datos.groupby(SUBJECT_COLUMN):
        for indicador in INDICADORES:
            r = stats.spearmanr(g[indicador], g[GRADE_PERCENT_COLUMN])
            filas.append({SUBJECT_COLUMN: materia, INDICATOR_COLUMN: indicador, STUDENTS_COLUMN: len(g),
                          SPEARMAN_COLUMN: r.statistic, P_VALUE_COLUMN: r.pvalue})
    res = pd.DataFrame(filas)
    res[SIGNIFICANT_COLUMN] = res[P_VALUE_COLUMN] < SIGNIFICANCE_LEVEL
    return res.round({SPEARMAN_COLUMN: SPEARMAN_DECIMALS, P_VALUE_COLUMN: P_VALUE_DECIMALS})


def matriz_correlaciones(correlaciones: pd.DataFrame) -> pd.DataFrame:
    return correlaciones.pivot(index=INDICATOR_COLUMN, columns=SUBJECT_COLUMN, values=SPEARMAN_COLUMN).reindex(INDICADORES)


def indicador_mas_relacionado(correlaciones: pd.DataFrame) -> str:
    return correlaciones.assign(**{ABSOLUTE_R_COLUMN: correlaciones[SPEARMAN_COLUMN].abs()}).groupby(INDICATOR_COLUMN)[ABSOLUTE_R_COLUMN].mean().idxmax()
