from pathlib import Path
import sys
import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[1])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
import constants as const


CLAVES = const.KEY_COLUMNS

CONDICIONES_PUNTOS = const.CONDITION_POINTS
CONDICIONES = const.CONDITIONS

UMBRALES_PCT = {
    materia: {const.CONDITION_REGULAR: regular / total * const.PERCENT_FACTOR, const.CONDITION_PROMOTED: promociona / total * const.PERCENT_FACTOR}
    for materia, (total, regular, promociona) in CONDICIONES_PUNTOS.items()
}

ASIGNATURAS_ACUMULATIVAS = const.CUMULATIVE_SUBJECT_KEYS


def _solo_matriculados(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    matriculados = cruce.loc[cruce[const.ENROLLED_COLUMN], CLAVES]
    return calificaciones.merge(matriculados, on=CLAVES, how="inner")

def _con_nota_valida(calificaciones: pd.DataFrame) -> pd.DataFrame:
    return calificaciones[calificaciones[const.MAXIMUM_COLUMN] > 0].dropna(
        subset=[const.OBTAINED_COLUMN, const.MAXIMUM_COLUMN])

def nota_por_estudiante(calificaciones: pd.DataFrame) -> pd.DataFrame:
    res = (
        _con_nota_valida(calificaciones).groupby(CLAVES)
        .agg(**{const.INSTRUMENT_COUNT_COLUMN: (const.MAXIMUM_COLUMN, "size"), const.POINTS_OBTAINED_COLUMN: (const.OBTAINED_COLUMN, "sum"), const.POINTS_POSSIBLE_COLUMN: (const.MAXIMUM_COLUMN, "sum")})
        .reset_index()
    )
    res[const.GRADE_PERCENT_COLUMN] = res[const.POINTS_OBTAINED_COLUMN] / res[const.POINTS_POSSIBLE_COLUMN] * const.PERCENT_FACTOR
    return res

def promedio_general_por_asignatura(
        calificaciones: pd.DataFrame, cruce: pd.DataFrame, matriculados: bool = True) -> pd.DataFrame:
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    return (
        nota_por_estudiante(calificaciones).groupby(const.SUBJECT_COLUMN)[const.GRADE_PERCENT_COLUMN]
        .agg(**{const.STUDENTS_COLUMN: "size", const.AVERAGE_PERCENT_COLUMN: "mean", const.MEDIAN_PERCENT_COLUMN: "median"})
        .round(const.ROUND_DECIMALS)
        .reset_index()
    )

def promedio_por_tipo_evaluacion(
        calificaciones: pd.DataFrame, cruce: pd.DataFrame, matriculados: bool = True) -> pd.DataFrame:
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    por_estudiante = (
        _con_nota_valida(calificaciones).groupby(
            [const.SUBJECT_COLUMN, const.EVALUATION_TYPE_COLUMN, const.USER_COLUMN])
        .agg(**{const.OBTAINED_SUM_COLUMN: (const.OBTAINED_COLUMN, "sum"), const.POSSIBLE_SUM_COLUMN: (const.MAXIMUM_COLUMN, "sum"), const.MAXIMUM_COLUMN: (const.MAXIMUM_COLUMN, "max")})
        .reset_index()
    )
    por_estudiante[const.GRADE_PERCENT_COLUMN] = por_estudiante[const.OBTAINED_SUM_COLUMN] / por_estudiante[const.POSSIBLE_SUM_COLUMN] * const.PERCENT_FACTOR
    return (
        por_estudiante.groupby([const.SUBJECT_COLUMN, const.EVALUATION_TYPE_COLUMN])
        .agg(**{const.STUDENTS_COLUMN: (const.USER_COLUMN, "size"), const.MAXIMUM_COLUMN: (const.MAXIMUM_COLUMN, "max"), const.AVERAGE_PERCENT_COLUMN: (const.GRADE_PERCENT_COLUMN, "mean")})
        .round(const.ROUND_DECIMALS)
        .reset_index()
    )

def distribucion_de_notas(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                          ancho_bin: int = const.DEFAULT_GRADE_BIN_WIDTH, matriculados: bool = True) -> pd.DataFrame:
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    por_estudiante = nota_por_estudiante(calificaciones)

    bordes = list(range(0, const.GRADE_SCALE_MAX + ancho_bin, ancho_bin))
    rangos = pd.IntervalIndex.from_breaks(bordes, closed="left")
    por_estudiante[const.RANGE_SOURCE_COLUMN] = pd.cut(
        por_estudiante[const.GRADE_PERCENT_COLUMN].clip(upper=bordes[-1] - const.GRADE_TOLERANCE), bins=rangos)

    conteo = (
        por_estudiante.groupby([const.SUBJECT_COLUMN, const.RANGE_SOURCE_COLUMN], observed=False).size()
        .rename(const.STUDENTS_COLUMN).reset_index()
    )
    conteo[const.DISTRIBUTION_FROM_COLUMN] = conteo[const.RANGE_SOURCE_COLUMN].map(lambda r: int(r.left))
    conteo[const.DISTRIBUTION_TO_COLUMN] = conteo[const.RANGE_SOURCE_COLUMN].map(lambda r: int(r.right))
    conteo[const.RANGE_SOURCE_COLUMN] = conteo[const.DISTRIBUTION_FROM_COLUMN].astype(str) + "-" + conteo[const.DISTRIBUTION_TO_COLUMN].astype(str)
    conteo[const.PERCENTAGE_COLUMN] = (conteo[const.STUDENTS_COLUMN] / conteo.groupby(const.SUBJECT_COLUMN)[const.STUDENTS_COLUMN].transform("sum") * const.PERCENT_FACTOR).round(const.ROUND_DECIMALS)
    return conteo[[const.SUBJECT_COLUMN, const.RANGE_SOURCE_COLUMN, const.DISTRIBUTION_FROM_COLUMN, const.DISTRIBUTION_TO_COLUMN, const.STUDENTS_COLUMN, const.PERCENTAGE_COLUMN]]

def condicion_por_estudiante(
        calificaciones: pd.DataFrame, cruce: pd.DataFrame, matriculados: bool = True) -> pd.DataFrame:
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    res = nota_por_estudiante(calificaciones)
    regular = res[const.SUBJECT_COLUMN].map(lambda m: UMBRALES_PCT[m][const.CONDITION_REGULAR])
    promociona = res[const.SUBJECT_COLUMN].map(lambda m: UMBRALES_PCT[m][const.CONDITION_PROMOTED])
    eps = const.GRADE_TOLERANCE
    res[const.CONDITION_COLUMN] = const.CONDITION_FREE
    res.loc[res[const.GRADE_PERCENT_COLUMN] + eps >= regular, const.CONDITION_COLUMN] = const.CONDITION_REGULAR
    res.loc[res[const.GRADE_PERCENT_COLUMN] + eps >= promociona, const.CONDITION_COLUMN] = const.CONDITION_PROMOTED
    return res

def condicion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame, matriculados: bool = True) -> pd.DataFrame:
    por_estudiante = condicion_por_estudiante(calificaciones, cruce, matriculados)
    conteo = (
        por_estudiante.groupby([const.SUBJECT_COLUMN, const.CONDITION_COLUMN]).size().unstack(fill_value=0)
        .reindex(columns=CONDICIONES, fill_value=0)
        .stack().rename(const.STUDENTS_COLUMN).reset_index()
    )
    conteo[const.PERCENTAGE_COLUMN] = (conteo[const.STUDENTS_COLUMN] / conteo.groupby(const.SUBJECT_COLUMN)[const.STUDENTS_COLUMN].transform("sum") * const.PERCENT_FACTOR).round(const.ROUND_DECIMALS)
    return conteo

def comparar_asignaturas(calificaciones: pd.DataFrame, cruce: pd.DataFrame, matriculados: bool = True) -> pd.DataFrame:
    por_estudiante = condicion_por_estudiante(calificaciones, cruce, matriculados)
    general = por_estudiante[const.GRADE_PERCENT_COLUMN].mean()

    res = por_estudiante.groupby(const.SUBJECT_COLUMN).agg(
        **{const.STUDENTS_COLUMN: (const.USER_COLUMN, "size"), const.AVERAGE_PERCENT_COLUMN: (const.GRADE_PERCENT_COLUMN, "mean"), const.MEDIAN_PERCENT_COLUMN: (const.GRADE_PERCENT_COLUMN, "median"), const.STD_PERCENT_COLUMN: (const.GRADE_PERCENT_COLUMN, "std"), const.POINTS_EVALUATED_COLUMN: (const.POINTS_POSSIBLE_COLUMN, "mean")},
    )
    res[const.DIFF_VS_GENERAL_COLUMN] = res[const.AVERAGE_PERCENT_COLUMN] - general
    totales = pd.Series({m: CONDICIONES_PUNTOS[m][0] for m in ASIGNATURAS_ACUMULATIVAS})
    res[const.EVALUATION_PROGRESS_COLUMN] = res[const.POINTS_EVALUATED_COLUMN] / totales * const.PERCENT_FACTOR

    condicion = condicion_academica(calificaciones, cruce, matriculados).pivot(
        index=const.SUBJECT_COLUMN, columns=const.CONDITION_COLUMN, values=const.PERCENTAGE_COLUMN)
    res[const.PROMOTED_PERCENT_COLUMN] = condicion[const.CONDITION_PROMOTED]
    res[const.REGULAR_PERCENT_COLUMN] = condicion[const.CONDITION_REGULAR]
    res[const.FREE_PERCENT_COLUMN] = condicion[const.CONDITION_FREE]

    columnas = [const.STUDENTS_COLUMN, const.AVERAGE_PERCENT_COLUMN, const.MEDIAN_PERCENT_COLUMN, const.STD_PERCENT_COLUMN, const.DIFF_VS_GENERAL_COLUMN,
                const.PROMOTED_PERCENT_COLUMN, const.REGULAR_PERCENT_COLUMN, const.FREE_PERCENT_COLUMN, const.EVALUATION_PROGRESS_COLUMN]
    return res[columnas].round(const.ROUND_DECIMALS).reset_index()
