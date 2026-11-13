from typing import Dict, List

import pandas as pd

from data.real_common import (
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrolled_traceability,
    load_enrollment_cross,
    load_grades,
    load_participation,
)
from kpis.kpis_calificaciones import distribucion_de_notas, promedio_general_por_asignatura
from kpis.kpis_participacion import estudiantes_activos_vs_inactivos, sesiones_promedio_por_estudiante
from kpis.kpis_trazabilidad import frecuencia_ingreso

SUBJECT_COLUMN: str = "materia"
USER_COLUMN: str = "usuario"
ENROLLED_COLUMN: str = "matriculado"
PERIOD_COLUMN: str = "periodo"
WEEKLY_SESSIONS_SOURCE_COLUMN: str = "ingresos_por_usuario_activo"
DISTRIBUTION_FROM_COLUMN: str = "desde"
DISTRIBUTION_TO_COLUMN: str = "hasta"
DISTRIBUTION_COUNT_COLUMN: str = "estudiantes"
STATUS_COLUMN: str = "status"
COUNT_COLUMN: str = "count"
RANGE_COLUMN: str = "range"
WEEK_COLUMN: str = "week"
SESSIONS_COLUMN: str = "sessions"

WEEKLY_FREQUENCY: str = "W"
WEEK_PREFIX: str = "Sem"
ACTIVE_LABEL: str = "Activos"
INACTIVE_LABEL: str = "Inactivos"

SCALE_DIVISOR: int = 10
DISTRIBUTION_BIN_WIDTH: int = 20
ONE_DECIMAL_FORMAT: str = ".1f"
INTEGER_FORMAT: str = ".0f"

def select_row(table: pd.DataFrame, subject: str) -> pd.Series:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = table[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = table.loc[is_subject]
    row: pd.Series = selected.iloc[0]

    return row

def keep_enrolled_participation(participation: pd.DataFrame, enrollment_cross: pd.DataFrame) -> pd.DataFrame:
    pair_columns: list = [SUBJECT_COLUMN, USER_COLUMN]
    is_enrolled: pd.Series = enrollment_cross[ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    enrolled_pairs: pd.DataFrame = enrolled_rows[pair_columns]
    result: pd.DataFrame = participation.merge(enrolled_pairs, on=pair_columns, how="inner")

    return result

def build_cards(subject: str, active_table: pd.DataFrame, grades_table: pd.DataFrame, sessions_table: pd.DataFrame) -> List[Dict[str, str]]:
    active_row: pd.Series = select_row(table=active_table, subject=subject)
    grades_row: pd.Series = select_row(table=grades_table, subject=subject)
    sessions_row: pd.Series = select_row(table=sessions_table, subject=subject)
    enrolled_text: str = str(int(sessions_row["matriculados"]))
    active_text: str = str(int(active_row["activos"]))
    inactive_text: str = str(int(active_row["inactivos"]))
    active_percent: str = format(float(active_row["pct_activos"]), INTEGER_FORMAT)
    inactive_percent: str = format(float(active_row["pct_inactivos"]), INTEGER_FORMAT)
    grade_value: float = float(grades_row["promedio_pct"]) / SCALE_DIVISOR
    grade_text: str = format(grade_value, ONE_DECIMAL_FORMAT)
    sessions_text: str = format(float(sessions_row["promedio_activos"]), ONE_DECIMAL_FORMAT)
    active_detail: str = f"{active_percent}% de la matrícula"
    inactive_detail: str = f"{inactive_percent}% de la matrícula"
    cards: List[Dict[str, str]] = [
        {"title": "Matriculados", "value": enrolled_text, "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": active_text, "detail": active_detail},
        {"title": "Inactivos", "value": inactive_text, "detail": inactive_detail},
        {"title": "Promedio de notas", "value": grade_text, "detail": "Escala de 0 a 10"},
        {"title": "Promedio de sesiones", "value": sessions_text, "detail": "Por estudiante activo"},
    ]

    return cards

def build_active_inactive(active_table: pd.DataFrame, subject: str) -> pd.DataFrame:
    active_row: pd.Series = select_row(table=active_table, subject=subject)
    active_count: int = int(active_row["activos"])
    inactive_count: int = int(active_row["inactivos"])
    table_data: Dict[str, list] = {
        STATUS_COLUMN: [ACTIVE_LABEL, INACTIVE_LABEL],
        COUNT_COLUMN: [active_count, inactive_count],
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_range_label(row_from: int, row_to: int) -> str:
    label_from: int = row_from // SCALE_DIVISOR
    label_to: int = row_to // SCALE_DIVISOR
    label: str = f"{label_from}-{label_to}"

    return label

def build_grade_distribution(distribution: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = distribution[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = distribution.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(DISTRIBUTION_FROM_COLUMN)
    labels: List[str] = []

    for row in sorted_rows.itertuples(index=False):
        row_from: int = getattr(row, DISTRIBUTION_FROM_COLUMN)
        row_to: int = getattr(row, DISTRIBUTION_TO_COLUMN)
        label: str = build_range_label(row_from=row_from, row_to=row_to)
        labels.append(label)

    counts: List[int] = sorted_rows[DISTRIBUTION_COUNT_COLUMN].tolist()
    table_data: Dict[str, list] = {
        RANGE_COLUMN: labels,
        COUNT_COLUMN: counts,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_participation_trend(weekly: pd.DataFrame, subject: str) -> pd.DataFrame:
    subject_key: str = SUBJECT_KEYS[subject]
    is_subject: pd.Series = weekly[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = weekly.loc[is_subject]
    sorted_rows: pd.DataFrame = selected.sort_values(PERIOD_COLUMN)
    values: List[float] = sorted_rows[WEEKLY_SESSIONS_SOURCE_COLUMN].tolist()
    weeks: List[str] = []
    week_number: int = 1

    for value in values:
        week_label: str = f"{WEEK_PREFIX} {week_number}"
        weeks.append(week_label)
        week_number = week_number + 1

    table_data: Dict[str, list] = {
        WEEK_COLUMN: weeks,
        SESSIONS_COLUMN: values,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_all() -> Dict[str, Dict[str, object]]:
    participation: pd.DataFrame = load_participation()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    traceability: pd.DataFrame = load_enrolled_traceability()
    enrolled_participation: pd.DataFrame = keep_enrolled_participation(participation=participation, enrollment_cross=enrollment_cross)
    active_table: pd.DataFrame = estudiantes_activos_vs_inactivos(participacion=enrolled_participation, cruce=enrollment_cross)
    grades_table: pd.DataFrame = promedio_general_por_asignatura(calificaciones=grades, cruce=enrollment_cross, matriculados=True)
    sessions_table: pd.DataFrame = sesiones_promedio_por_estudiante(trazabilidad=traceability, cruce=enrollment_cross)
    distribution: pd.DataFrame = distribucion_de_notas(calificaciones=grades, cruce=enrollment_cross, ancho_bin=DISTRIBUTION_BIN_WIDTH, matriculados=True)
    weekly: pd.DataFrame = frecuencia_ingreso(df=traceability, freq=WEEKLY_FREQUENCY)
    cards: Dict[str, List[Dict[str, str]]] = {}
    active_inactive: Dict[str, pd.DataFrame] = {}
    distributions: Dict[str, pd.DataFrame] = {}
    trends: Dict[str, pd.DataFrame] = {}

    for subject in SUBJECTS:
        cards[subject] = build_cards(subject=subject, active_table=active_table, grades_table=grades_table, sessions_table=sessions_table)
        active_inactive[subject] = build_active_inactive(active_table=active_table, subject=subject)
        distributions[subject] = build_grade_distribution(distribution=distribution, subject=subject)
        trends[subject] = build_participation_trend(weekly=weekly, subject=subject)

    result: Dict[str, Dict[str, object]] = {
        "cards": cards,
        "active_inactive": active_inactive,
        "distribution": distributions,
        "trend": trends,
    }

    return result

ALL_TABLES: Dict[str, Dict[str, object]] = build_all()

GENERAL_KPIS: Dict[str, List[Dict[str, str]]] = ALL_TABLES["cards"]

ACTIVE_INACTIVE: Dict[str, pd.DataFrame] = ALL_TABLES["active_inactive"]

GRADE_DISTRIBUTION: Dict[str, pd.DataFrame] = ALL_TABLES["distribution"]

PARTICIPATION_TREND: Dict[str, pd.DataFrame] = ALL_TABLES["trend"]

GENERAL_INTERPRETATION: str = (
    "Las tres asignaturas muestran una participación creciente a lo largo del "
    "período. Algoritmos y Estructuras de Datos concentra la mayor matrícula y el "
    "mayor promedio de sesiones, mientras que Probabilidad y Estadística presenta "
    "la proporción más alta de estudiantes inactivos."
)
