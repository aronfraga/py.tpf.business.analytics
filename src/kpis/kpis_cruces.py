"""Cruces analíticos: relación de la participación y la trazabilidad con las notas.

Entrada : data/integrado/{participacion,trazabilidad,calificaciones,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).
Requiere: scipy (pruebas de significancia). Está en requirements.txt.

Criterios comunes:
  - Universo: estudiantes matriculados, una fila por estudiante y asignatura.
  - Nota (`nota_pct`): porcentaje del total de puntos rendidos (ver kpis_calificaciones.py). A quienes
    no se presentaron a ningún instrumento se les asigna 0 y se los marca con `se_presento = False`.
  - Participación: tiempo acumulado en la plataforma, en minutos (ver kpis_participacion.py).
  - Trazabilidad: indicadores de uso (días activos, ingresos, semanas activas, interacciones con el
    material y en foros). Se excluyen las interacciones de evaluaciones y calificaciones, porque son
    consecuencia de presentarse a evaluar.

La justificación y los controles de cada cruce están en cruce_participacion_notas.ipynb.
"""
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

try:  # como paquete (kpis.kpis_cruces) o como módulo suelto (kpis_cruces)
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


# ----------------------------------------------------------------------------
# Cruce 1: participación (tiempo en la plataforma) vs. notas
# ----------------------------------------------------------------------------
def participacion_vs_notas(participacion: pd.DataFrame, calificaciones: pd.DataFrame,
                           cruce: pd.DataFrame) -> pd.DataFrame:
    """Participación y nota de cada estudiante matriculado, por asignatura.

    A quienes no se presentaron a ningún instrumento se les asigna nota 0.

    Devuelve: materia, usuario, tiempo_min (tiempo acumulado en la plataforma, en minutos),
    nota_pct (0-100) y se_presento (False si no rindió ningún instrumento).
    """
    tiempo = tiempo_por_estudiante(participacion, cruce)
    notas = nota_por_estudiante(calificaciones)[CLAVES + [GRADE_PERCENT_COLUMN]]
    res = tiempo.merge(notas, on=CLAVES, how="left")
    res[PRESENTED_COLUMN] = res[GRADE_PERCENT_COLUMN].notna()
    res[GRADE_PERCENT_COLUMN] = res[GRADE_PERCENT_COLUMN].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)


def correlacion_participacion_nota(tabla: pd.DataFrame) -> pd.DataFrame:
    """Correlación entre tiempo en la plataforma y nota, por asignatura.

    Se calcula con todas las filas de la tabla recibida. Para ver solo a quienes se presentaron,
    se filtra antes: `correlacion_participacion_nota(tabla[tabla["se_presento"]])`.

    Devuelve: materia, estudiantes, pearson, spearman, pendiente_pp_por_hora (puntos porcentuales
    de nota por cada hora adicional, regresión lineal simple).
    """
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
    """Recta de tendencia (regresión lineal) de la nota según el tiempo, por asignatura.

    Devuelve dos puntos por asignatura: materia, tiempo_min, nota_pct. Tiene las mismas columnas
    que la tabla de puntos, para graficar ambas juntas. La recta se
    limita al rango válido de la nota (0 a 100): si el ajuste supera 100 antes del tiempo máximo
    observado, el segundo punto se corta donde la recta llega a 100.
    """
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
    """Nota promedio según el tramo de tiempo en la plataforma, por asignatura.

    Los estudiantes se dividen en `tramos` grupos de igual tamaño según su tiempo (cuartiles por
    defecto; el tramo 1 es el de menor participación).

    Devuelve: materia, tramo, tiempo_desde_min, tiempo_hasta_min, estudiantes, nota_promedio_pct.
    """
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


# ----------------------------------------------------------------------------
# Cruce 2: tiempo de conexión vs. calificación final
# ----------------------------------------------------------------------------
def prueba_de_correlacion(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    """Correlación entre tiempo de conexión y calificación final, con pruebas de significancia.

    Con `solo_presentados=True` se excluye a quienes no rindieron ningún instrumento.

    Devuelve: materia, estudiantes, pearson, pearson_ic95_inf, pearson_ic95_sup, pearson_p,
    spearman, spearman_p y significativa (ambos p-valores < 0,05).
    """
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
    """Agrega a la tabla por alumno su condición académica (promocionado, regular, libre o no se presentó)."""
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + [CONDITION_COLUMN]]
    res = tabla.merge(condicion, on=CLAVES, how="left")
    res[CONDITION_COLUMN] = res[CONDITION_COLUMN].fillna(CONDITION_NOT_PRESENTED)
    return res


def resumen_tiempo_por_condicion(tabla_condicion: pd.DataFrame) -> pd.DataFrame:
    """Tiempo en la plataforma por asignatura y condición.

    Devuelve: materia, condicion, estudiantes, promedio_min, mediana_min (incluye grupos vacíos).
    """
    res = (
        tabla_condicion.groupby([SUBJECT_COLUMN, CONDITION_COLUMN])[TIME_MINUTES_COLUMN]
        .agg(**{STUDENTS_COLUMN: "size", AVERAGE_MINUTES_COLUMN: "mean", MEDIAN_MINUTES_COLUMN: "median"})
    )
    completo = pd.MultiIndex.from_product([sorted(tabla_condicion[SUBJECT_COLUMN].unique()), GRUPOS], names=[SUBJECT_COLUMN, CONDITION_COLUMN])
    res = res.reindex(completo).reset_index()
    res[STUDENTS_COLUMN] = res[STUDENTS_COLUMN].fillna(0).astype(int)
    return res.round(1)


# ----------------------------------------------------------------------------
# Cruce 3: trazabilidad vs. rendimiento
# ----------------------------------------------------------------------------
def indicadores_de_trazabilidad(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                                minutos_inactividad: int = INACTIVITY_MINUTES) -> pd.DataFrame:
    """Indicadores de uso de la plataforma de cada estudiante matriculado, por asignatura.

    Devuelve: materia, usuario, dias_activos, ingresos, semanas_activas, interacciones_material,
    interacciones_foros. Quienes no tienen eventos quedan con 0.
    """
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
    """Indicadores de trazabilidad y nota de cada estudiante matriculado, por asignatura.

    Devuelve: materia, usuario, los indicadores de `indicadores_de_trazabilidad`, nota_pct (0-100,
    con 0 para quienes no se presentaron) y se_presento.
    """
    notas = nota_por_estudiante(calificaciones)[CLAVES + [GRADE_PERCENT_COLUMN]]
    res = indicadores_de_trazabilidad(trazabilidad, cruce).merge(notas, on=CLAVES, how="left")
    res[PRESENTED_COLUMN] = res[GRADE_PERCENT_COLUMN].notna()
    res[GRADE_PERCENT_COLUMN] = res[GRADE_PERCENT_COLUMN].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)


def correlaciones_trazabilidad_nota(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    """Correlación de Spearman entre cada indicador de trazabilidad y la nota, por asignatura.

    Con `solo_presentados=True` se excluye a quienes no rindieron ningún instrumento.

    Devuelve (una fila por asignatura e indicador): materia, indicador, estudiantes, spearman,
    p_valor y significativa (p_valor < 0,05).
    """
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
    """Matriz indicador (filas) x asignatura (columnas) con la correlación, para `heatmap`."""
    return correlaciones.pivot(index=INDICATOR_COLUMN, columns=SUBJECT_COLUMN, values=SPEARMAN_COLUMN).reindex(INDICADORES)


def indicador_mas_relacionado(correlaciones: pd.DataFrame) -> str:
    """Indicador con mayor |correlación| promedio entre asignaturas."""
    return correlaciones.assign(**{ABSOLUTE_R_COLUMN: correlaciones[SPEARMAN_COLUMN].abs()}).groupby(INDICATOR_COLUMN)[ABSOLUTE_R_COLUMN].mean().idxmax()
