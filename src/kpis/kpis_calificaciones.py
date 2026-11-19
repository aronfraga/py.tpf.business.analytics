"""KPIs de calificaciones: promedio general, distribución de notas, condición académica y comparación.

Entrada : data/integrado/{calificaciones,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).

Las funciones de KPI son puras (reciben y devuelven DataFrames).

Criterio de nota: cada estudiante tiene una nota en porcentaje (0-100) calculada como
    suma(nota_obtenida) / suma(nota_max) * 100
sobre los instrumentos que rindió. Así se respetan los distintos pesos de cada instrumento y las
distintas escalas de cada asignatura, y los datos nuevos (un parcial, un recuperatorio) se suman
solos. Los umbrales de condición también se expresan como porcentaje del total posible.

La justificación y los controles de cada KPI están en calificaciones.ipynb.
"""
import sys
from pathlib import Path

import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[1])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
from constants import (
    AVERAGE_PERCENT_COLUMN,
    CONDITIONS,
    CONDITION_COLUMN,
    CONDITION_FREE,
    CONDITION_POINTS,
    CONDITION_PROMOTED,
    CONDITION_REGULAR,
    CUMULATIVE_SUBJECT_KEYS,
    DEFAULT_GRADE_BIN_WIDTH,
    DIFF_VS_GENERAL_COLUMN,
    DISTRIBUTION_FROM_COLUMN,
    DISTRIBUTION_TO_COLUMN,
    ENROLLED_COLUMN,
    EVALUATION_PROGRESS_COLUMN,
    EVALUATION_TYPE_COLUMN,
    FREE_PERCENT_COLUMN,
    GRADE_PERCENT_COLUMN,
    GRADE_SCALE_MAX,
    GRADE_TOLERANCE,
    INSTRUMENT_COUNT_COLUMN,
    KEY_COLUMNS,
    MAXIMUM_COLUMN,
    MEDIAN_PERCENT_COLUMN,
    OBTAINED_COLUMN,
    OBTAINED_SUM_COLUMN,
    PERCENTAGE_COLUMN,
    PERCENT_FACTOR,
    POINTS_EVALUATED_COLUMN,
    POINTS_OBTAINED_COLUMN,
    POINTS_POSSIBLE_COLUMN,
    POSSIBLE_SUM_COLUMN,
    PROMOTED_PERCENT_COLUMN,
    RANGE_SOURCE_COLUMN,
    REGULAR_PERCENT_COLUMN,
    ROUND_DECIMALS,
    STD_PERCENT_COLUMN,
    STUDENTS_COLUMN,
    SUBJECT_COLUMN,
    USER_COLUMN,
)


CLAVES = KEY_COLUMNS

# Condiciones de cada asignatura en puntos: (total posible, mínimo para regular, mínimo para promocionar)
CONDICIONES_PUNTOS = CONDITION_POINTS
CONDICIONES = CONDITIONS

# Los mismos umbrales como porcentaje del total posible
UMBRALES_PCT = {
    materia: {CONDITION_REGULAR: regular / total * PERCENT_FACTOR, CONDITION_PROMOTED: promociona / total * PERCENT_FACTOR}
    for materia, (total, regular, promociona) in CONDICIONES_PUNTOS.items()
}

# Asignaturas cuya nota final es la suma de puntos (las demás promedian sus instrumentos)
ASIGNATURAS_ACUMULATIVAS = CUMULATIVE_SUBJECT_KEYS


# ----------------------------------------------------------------------------
# Auxiliares
# ----------------------------------------------------------------------------
def _solo_matriculados(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Deja únicamente las calificaciones de estudiantes matriculados en esa asignatura."""
    matriculados = cruce.loc[cruce[ENROLLED_COLUMN], CLAVES]
    return calificaciones.merge(matriculados, on=CLAVES, how="inner")


def _con_nota_valida(calificaciones: pd.DataFrame) -> pd.DataFrame:
    """Descarta filas sin nota o sin máximo válido (nulo o <= 0)."""
    return calificaciones[calificaciones[MAXIMUM_COLUMN] > 0].dropna(subset=[OBTAINED_COLUMN, MAXIMUM_COLUMN])


# ----------------------------------------------------------------------------
# KPI 1: promedio general por asignatura
# ----------------------------------------------------------------------------
def nota_por_estudiante(calificaciones: pd.DataFrame) -> pd.DataFrame:
    """Nota (0-100) de cada estudiante en cada asignatura sobre el total de puntos posibles.

    Devuelve: materia, usuario, instrumentos, puntos_obtenidos, puntos_posibles, nota_pct.
    """
    res = (
        _con_nota_valida(calificaciones).groupby(CLAVES)
        .agg(**{INSTRUMENT_COUNT_COLUMN: (MAXIMUM_COLUMN, "size"), POINTS_OBTAINED_COLUMN: (OBTAINED_COLUMN, "sum"), POINTS_POSSIBLE_COLUMN: (MAXIMUM_COLUMN, "sum")})
        .reset_index()
    )
    res[GRADE_PERCENT_COLUMN] = res[POINTS_OBTAINED_COLUMN] / res[POINTS_POSSIBLE_COLUMN] * PERCENT_FACTOR
    return res


def promedio_general_por_asignatura(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                                    matriculados: bool = True) -> pd.DataFrame:
    """KPI: promedio general por asignatura, en porcentaje del máximo posible (0-100).

    Devuelve una fila por asignatura: materia, estudiantes, promedio_pct (promedio de la nota
    de cada estudiante, así cada estudiante pesa igual) y mediana_pct.
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    return (
        nota_por_estudiante(calificaciones).groupby(SUBJECT_COLUMN)[GRADE_PERCENT_COLUMN]
        .agg(**{STUDENTS_COLUMN: "size", AVERAGE_PERCENT_COLUMN: "mean", MEDIAN_PERCENT_COLUMN: "median"})
        .round(ROUND_DECIMALS)
        .reset_index()
    )


def promedio_por_tipo_evaluacion(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                                 matriculados: bool = True) -> pd.DataFrame:
    """Promedio (0-100) por asignatura y tipo de evaluación, con el máximo original del instrumento.

    Devuelve: materia, tipo_evaluacion, estudiantes, nota_max, promedio_pct.
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    por_estudiante = (
        _con_nota_valida(calificaciones).groupby([SUBJECT_COLUMN, EVALUATION_TYPE_COLUMN, USER_COLUMN])
        .agg(**{OBTAINED_SUM_COLUMN: (OBTAINED_COLUMN, "sum"), POSSIBLE_SUM_COLUMN: (MAXIMUM_COLUMN, "sum"), MAXIMUM_COLUMN: (MAXIMUM_COLUMN, "max")})
        .reset_index()
    )
    por_estudiante[GRADE_PERCENT_COLUMN] = por_estudiante[OBTAINED_SUM_COLUMN] / por_estudiante[POSSIBLE_SUM_COLUMN] * PERCENT_FACTOR
    return (
        por_estudiante.groupby([SUBJECT_COLUMN, EVALUATION_TYPE_COLUMN])
        .agg(**{STUDENTS_COLUMN: (USER_COLUMN, "size"), MAXIMUM_COLUMN: (MAXIMUM_COLUMN, "max"), AVERAGE_PERCENT_COLUMN: (GRADE_PERCENT_COLUMN, "mean")})
        .round(ROUND_DECIMALS)
        .reset_index()
    )


# ----------------------------------------------------------------------------
# KPI 2: distribución de notas (histograma)
# ----------------------------------------------------------------------------
def distribucion_de_notas(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                          ancho_bin: int = DEFAULT_GRADE_BIN_WIDTH, matriculados: bool = True) -> pd.DataFrame:
    """KPI: distribución de notas por asignatura, en rangos de `ancho_bin` puntos sobre 100.

    Los rangos son [0, ancho), [ancho, 2*ancho), ..., y el último incluye el 100. Cada estudiante
    cuenta una vez por asignatura. Incluye los rangos vacíos. Es el insumo del histograma de
    Streamlit (`histogram(tabla[tabla["materia"] == m], "rango", "estudiantes", ...)`).

    Devuelve (una fila por asignatura y rango): materia, rango (texto, p. ej. "80-90"), desde,
    hasta, estudiantes, porcentaje (de los estudiantes de la asignatura).
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    por_estudiante = nota_por_estudiante(calificaciones)

    bordes = list(range(0, GRADE_SCALE_MAX + ancho_bin, ancho_bin))
    rangos = pd.IntervalIndex.from_breaks(bordes, closed="left")
    # Un 100 exacto va al último rango
    por_estudiante[RANGE_SOURCE_COLUMN] = pd.cut(por_estudiante[GRADE_PERCENT_COLUMN].clip(upper=bordes[-1] - GRADE_TOLERANCE), bins=rangos)

    conteo = (
        por_estudiante.groupby([SUBJECT_COLUMN, RANGE_SOURCE_COLUMN], observed=False).size()
        .rename(STUDENTS_COLUMN).reset_index()
    )
    conteo[DISTRIBUTION_FROM_COLUMN] = conteo[RANGE_SOURCE_COLUMN].map(lambda r: int(r.left))
    conteo[DISTRIBUTION_TO_COLUMN] = conteo[RANGE_SOURCE_COLUMN].map(lambda r: int(r.right))
    conteo[RANGE_SOURCE_COLUMN] = conteo[DISTRIBUTION_FROM_COLUMN].astype(str) + "-" + conteo[DISTRIBUTION_TO_COLUMN].astype(str)
    conteo[PERCENTAGE_COLUMN] = (conteo[STUDENTS_COLUMN] / conteo.groupby(SUBJECT_COLUMN)[STUDENTS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return conteo[[SUBJECT_COLUMN, RANGE_SOURCE_COLUMN, DISTRIBUTION_FROM_COLUMN, DISTRIBUTION_TO_COLUMN, STUDENTS_COLUMN, PERCENTAGE_COLUMN]]


# ----------------------------------------------------------------------------
# KPI 3: promocionados, regulares y libres
# ----------------------------------------------------------------------------
def condicion_por_estudiante(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                             matriculados: bool = True) -> pd.DataFrame:
    """Condición (promocionado / regular / libre) de cada estudiante según su nota_pct.

    La nota es un porcentaje de lo rendido hasta ahora, así que quien tiene 30 de 30 puntos
    queda promocionado y no libre. Es una clasificación del desempeño actual, no una proyección.

    Devuelve: materia, usuario, instrumentos, puntos_obtenidos, puntos_posibles, nota_pct, condicion.
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    res = nota_por_estudiante(calificaciones)
    regular = res[SUBJECT_COLUMN].map(lambda m: UMBRALES_PCT[m][CONDITION_REGULAR])
    promociona = res[SUBJECT_COLUMN].map(lambda m: UMBRALES_PCT[m][CONDITION_PROMOTED])
    # Pequeña tolerancia para que 85 puntos sobre 120 (70,8333...) no quede afuera por redondeo
    eps = GRADE_TOLERANCE
    res[CONDITION_COLUMN] = CONDITION_FREE
    res.loc[res[GRADE_PERCENT_COLUMN] + eps >= regular, CONDITION_COLUMN] = CONDITION_REGULAR
    res.loc[res[GRADE_PERCENT_COLUMN] + eps >= promociona, CONDITION_COLUMN] = CONDITION_PROMOTED
    return res


def condicion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                        matriculados: bool = True) -> pd.DataFrame:
    """KPI: estudiantes promocionados, regulares y libres por asignatura.

    Devuelve una fila por asignatura y condición (incluye las condiciones sin estudiantes):
    materia, condicion, estudiantes, porcentaje. Sirve directo para el gráfico de dona de Streamlit.
    """
    por_estudiante = condicion_por_estudiante(calificaciones, cruce, matriculados)
    conteo = (
        por_estudiante.groupby([SUBJECT_COLUMN, CONDITION_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=CONDICIONES, fill_value=0)
        .stack().rename(STUDENTS_COLUMN).reset_index()
    )
    conteo[PERCENTAGE_COLUMN] = (conteo[STUDENTS_COLUMN] / conteo.groupby(SUBJECT_COLUMN)[STUDENTS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return conteo


# ----------------------------------------------------------------------------
# KPI 4: comparación entre asignaturas
# ----------------------------------------------------------------------------
def comparar_asignaturas(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                         matriculados: bool = True) -> pd.DataFrame:
    """KPI: tabla comparativa de resultados por asignatura (todo en % del total posible).

    Reúne los KPI anteriores y agrega dispersión, diferencia contra el promedio general y
    avance de la evaluación. Al comparar hay que recordar que los umbrales para promocionar
    difieren entre asignaturas.

    Devuelve una fila por asignatura: materia, estudiantes, promedio_pct, mediana_pct, desvio_pct,
    dif_vs_general_pp (puntos porcentuales contra el promedio de todos los estudiantes),
    pct_promocionados, pct_regulares, pct_libres y avance_evaluacion_pct (parte del total de
    puntos ya evaluada; solo en asignaturas acumulativas, en las demás queda vacío).
    """
    por_estudiante = condicion_por_estudiante(calificaciones, cruce, matriculados)
    general = por_estudiante[GRADE_PERCENT_COLUMN].mean()

    res = por_estudiante.groupby(SUBJECT_COLUMN).agg(
        **{STUDENTS_COLUMN: (USER_COLUMN, "size"), AVERAGE_PERCENT_COLUMN: (GRADE_PERCENT_COLUMN, "mean"), MEDIAN_PERCENT_COLUMN: (GRADE_PERCENT_COLUMN, "median"), STD_PERCENT_COLUMN: (GRADE_PERCENT_COLUMN, "std"), POINTS_EVALUATED_COLUMN: (POINTS_POSSIBLE_COLUMN, "mean")},
    )
    res[DIFF_VS_GENERAL_COLUMN] = res[AVERAGE_PERCENT_COLUMN] - general
    totales = pd.Series({m: CONDICIONES_PUNTOS[m][0] for m in ASIGNATURAS_ACUMULATIVAS})
    res[EVALUATION_PROGRESS_COLUMN] = res[POINTS_EVALUATED_COLUMN] / totales * PERCENT_FACTOR

    condicion = condicion_academica(calificaciones, cruce, matriculados).pivot(
        index=SUBJECT_COLUMN, columns=CONDITION_COLUMN, values=PERCENTAGE_COLUMN
    )
    res[PROMOTED_PERCENT_COLUMN] = condicion[CONDITION_PROMOTED]
    res[REGULAR_PERCENT_COLUMN] = condicion[CONDITION_REGULAR]
    res[FREE_PERCENT_COLUMN] = condicion[CONDITION_FREE]

    columnas = [STUDENTS_COLUMN, AVERAGE_PERCENT_COLUMN, MEDIAN_PERCENT_COLUMN, STD_PERCENT_COLUMN, DIFF_VS_GENERAL_COLUMN,
                PROMOTED_PERCENT_COLUMN, REGULAR_PERCENT_COLUMN, FREE_PERCENT_COLUMN, EVALUATION_PROGRESS_COLUMN]
    return res[columnas].round(ROUND_DECIMALS).reset_index()
