from typing import Dict, List

import pandas as pd

from data.real_common import (
    ALGEBRA,
    ALGORITHMS,
    PROBABILITY,
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrolled_traceability,
    load_enrollment_cross,
    load_grades,
)
from kpis.kpis_calificaciones import nota_por_estudiante
from kpis.kpis_cruces import correlacion_participacion_nota, linea_de_tendencia
from kpis.kpis_participacion import sesiones_por_estudiante

SUBJECT_COLUMN: str = "materia"
USER_COLUMN: str = "usuario"
SESSIONS_SOURCE_COLUMN: str = "sesiones"
KPI_X_COLUMN: str = "tiempo_min"
GRADE_PERCENT_COLUMN: str = "nota_pct"
PRESENTED_COLUMN: str = "se_presento"
PEARSON_COLUMN: str = "pearson"
SESSIONS_COLUMN: str = "sessions"
GRADE_COLUMN: str = "grade"

SCALE_DIVISOR: int = 10
GRADE_DECIMALS: int = 2
VALUE_FORMAT: str = ".2f"
CARD_TITLE: str = "Correlación sesiones–nota"

NO_ASSOCIATION_LIMIT: float = 0.1
WEAK_LIMIT: float = 0.3
MODERATE_LIMIT: float = 0.5

def build_points_table(traceability: pd.DataFrame, grades: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.DataFrame:
    sessions: pd.DataFrame = sesiones_por_estudiante(trazabilidad=traceability, cruce=enrollment_cross)
    student_grades: pd.DataFrame = nota_por_estudiante(calificaciones=grades)
    pair_columns: list = [SUBJECT_COLUMN, USER_COLUMN]
    grade_columns: list = [SUBJECT_COLUMN, USER_COLUMN, GRADE_PERCENT_COLUMN]
    selected_grades: pd.DataFrame = student_grades[grade_columns]
    merged: pd.DataFrame = sessions.merge(selected_grades, on=pair_columns, how="left")
    merged[PRESENTED_COLUMN] = merged[GRADE_PERCENT_COLUMN].notna()
    filled_grades: pd.Series = merged[GRADE_PERCENT_COLUMN].fillna(0)
    merged[GRADE_PERCENT_COLUMN] = filled_grades
    rename_map: Dict[str, str] = {SESSIONS_SOURCE_COLUMN: KPI_X_COLUMN}
    result: pd.DataFrame = merged.rename(columns=rename_map)

    return result

def scale_grades(percent_values: pd.Series) -> List[float]:
    scaled: pd.Series = percent_values / SCALE_DIVISOR
    rounded: pd.Series = scaled.round(GRADE_DECIMALS)
    result: List[float] = rounded.tolist()

    return result

def build_xy_table(source: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = source[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = source.loc[is_subject]
    sessions: List[float] = selected[KPI_X_COLUMN].tolist()
    grades: List[float] = scale_grades(percent_values=selected[GRADE_PERCENT_COLUMN])
    table_data: Dict[str, list] = {
        SESSIONS_COLUMN: sessions,
        GRADE_COLUMN: grades,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def describe_strength(value: float) -> str:
    magnitude: float = abs(value)
    strength: str

    if magnitude < NO_ASSOCIATION_LIMIT:
        strength = "muy débil"
    elif magnitude < WEAK_LIMIT:
        strength = "débil"
    elif magnitude < MODERATE_LIMIT:
        strength = "moderada"
    else:
        strength = "fuerte"

    return strength

def describe_direction(value: float) -> str:
    direction: str

    if value >= 0:
        direction = "positiva"
    else:
        direction = "negativa"

    return direction

def build_card(correlations: pd.DataFrame, subject: str) -> Dict[str, str]:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = correlations[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = correlations.loc[is_subject]
    pearson: float = float(selected[PEARSON_COLUMN].iloc[0])
    value_text: str = format(pearson, VALUE_FORMAT)
    direction: str = describe_direction(value=pearson)
    strength: str = describe_strength(value=pearson)
    detail: str = f"Asociación {direction} {strength}"
    result: Dict[str, str] = {"title": CARD_TITLE, "value": value_text, "detail": detail}

    return result

def build_all() -> Dict[str, Dict[str, object]]:
    traceability: pd.DataFrame = load_enrolled_traceability()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    points_table: pd.DataFrame = build_points_table(
        traceability=traceability,
        grades=grades,
        enrollment_cross=enrollment_cross,
    )
    correlations: pd.DataFrame = correlacion_participacion_nota(tabla=points_table)
    trend_table: pd.DataFrame = linea_de_tendencia(tabla=points_table)
    scatter: Dict[str, pd.DataFrame] = {}
    trend: Dict[str, pd.DataFrame] = {}
    cards: Dict[str, Dict[str, str]] = {}

    for subject in SUBJECTS:
        scatter[subject] = build_xy_table(source=points_table, subject=subject)
        trend[subject] = build_xy_table(source=trend_table, subject=subject)
        cards[subject] = build_card(correlations=correlations, subject=subject)

    result: Dict[str, Dict[str, object]] = {
        "scatter": scatter,
        "trend": trend,
        "card": cards,
    }

    return result

ALL_TABLES: Dict[str, Dict[str, object]] = build_all()

SCATTER: Dict[str, pd.DataFrame] = ALL_TABLES["scatter"]

TREND_LINE: Dict[str, pd.DataFrame] = ALL_TABLES["trend"]

CORRELATION: Dict[str, Dict[str, str]] = ALL_TABLES["card"]

CORRELATION_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "A mayor cantidad de sesiones, las notas tienden a ser más altas. Algunos "
        "estudiantes con pocas sesiones obtienen notas medias."
    ),
    ALGORITHMS: (
        "La relación es la más fuerte de las tres asignaturas. Pocas sesiones se "
        "asocian con notas por debajo de 5."
    ),
    PROBABILITY: (
        "La relación es positiva, con mayor dispersión en el tramo medio de sesiones."
    ),
}
