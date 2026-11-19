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

CONDICIONES_PUNTOS = CONDITION_POINTS
CONDICIONES = CONDITIONS

UMBRALES_PCT = {
    materia: {CONDITION_REGULAR: regular / total * PERCENT_FACTOR, CONDITION_PROMOTED: promociona / total * PERCENT_FACTOR}
    for materia, (total, regular, promociona) in CONDICIONES_PUNTOS.items()
}

ASIGNATURAS_ACUMULATIVAS = CUMULATIVE_SUBJECT_KEYS


def _solo_matriculados(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    matriculados = cruce.loc[cruce[ENROLLED_COLUMN], CLAVES]
    return calificaciones.merge(matriculados, on=CLAVES, how="inner")


def _con_nota_valida(calificaciones: pd.DataFrame) -> pd.DataFrame:
    return calificaciones[calificaciones[MAXIMUM_COLUMN] > 0].dropna(subset=[OBTAINED_COLUMN, MAXIMUM_COLUMN])


def nota_por_estudiante(calificaciones: pd.DataFrame) -> pd.DataFrame:
    res = (
        _con_nota_valida(calificaciones).groupby(CLAVES)
        .agg(**{INSTRUMENT_COUNT_COLUMN: (MAXIMUM_COLUMN, "size"), POINTS_OBTAINED_COLUMN: (OBTAINED_COLUMN, "sum"), POINTS_POSSIBLE_COLUMN: (MAXIMUM_COLUMN, "sum")})
        .reset_index()
    )
    res[GRADE_PERCENT_COLUMN] = res[POINTS_OBTAINED_COLUMN] / res[POINTS_POSSIBLE_COLUMN] * PERCENT_FACTOR
    return res


def promedio_general_por_asignatura(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                                    matriculados: bool = True) -> pd.DataFrame:
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


def distribucion_de_notas(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                          ancho_bin: int = DEFAULT_GRADE_BIN_WIDTH, matriculados: bool = True) -> pd.DataFrame:
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    por_estudiante = nota_por_estudiante(calificaciones)

    bordes = list(range(0, GRADE_SCALE_MAX + ancho_bin, ancho_bin))
    rangos = pd.IntervalIndex.from_breaks(bordes, closed="left")
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


def condicion_por_estudiante(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                             matriculados: bool = True) -> pd.DataFrame:
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    res = nota_por_estudiante(calificaciones)
    regular = res[SUBJECT_COLUMN].map(lambda m: UMBRALES_PCT[m][CONDITION_REGULAR])
    promociona = res[SUBJECT_COLUMN].map(lambda m: UMBRALES_PCT[m][CONDITION_PROMOTED])
    eps = GRADE_TOLERANCE
    res[CONDITION_COLUMN] = CONDITION_FREE
    res.loc[res[GRADE_PERCENT_COLUMN] + eps >= regular, CONDITION_COLUMN] = CONDITION_REGULAR
    res.loc[res[GRADE_PERCENT_COLUMN] + eps >= promociona, CONDITION_COLUMN] = CONDITION_PROMOTED
    return res


def condicion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                        matriculados: bool = True) -> pd.DataFrame:
    por_estudiante = condicion_por_estudiante(calificaciones, cruce, matriculados)
    conteo = (
        por_estudiante.groupby([SUBJECT_COLUMN, CONDITION_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=CONDICIONES, fill_value=0)
        .stack().rename(STUDENTS_COLUMN).reset_index()
    )
    conteo[PERCENTAGE_COLUMN] = (conteo[STUDENTS_COLUMN] / conteo.groupby(SUBJECT_COLUMN)[STUDENTS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return conteo


def comparar_asignaturas(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                         matriculados: bool = True) -> pd.DataFrame:
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
